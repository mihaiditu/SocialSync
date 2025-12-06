# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
from fastapi.middleware.cors import CORSMiddleware
from rag_logic import SocialSyncAgent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import hashlib
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SESSION STORE
sessions = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str

class EventData(BaseModel):
    title: str
    date: str
    location: str
    cost: str
    description: str
    url: str

class ChatResponse(BaseModel):
    text: str
    events: List[EventData] = []
    mission_complete: bool = False

# --- HELPERS ---

def parse_event_text(raw_text):
    lines = raw_text.split('\n')
    info = {}
    for line in lines:
        if ": " in line:
            key, val = line.split(": ", 1)
            info[key.strip()] = val.strip()
    
    return EventData(
        title=info.get("Event", "Unknown"),
        date=info.get("Date", "TBD"),
        location=info.get("Location", "Check Link"),
        cost=info.get("Cost", "Free"),
        description=info.get("Description", ""),
        url=info.get("Source", "#")
    )

def strip_command_from_text(text):
    """
    Removes any line containing 'SEARCH_ACTION' from the text
    so the user doesn't see the robot commands.
    """
    lines = text.split('\n')
    # Keep only lines that DO NOT contain the command
    clean_lines = [line for line in lines if "SEARCH_ACTION" not in line.upper()]
    return "\n".join(clean_lines).strip()

# --- ENDPOINTS ---

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    # 1. Initialize Session
    if req.session_id not in sessions:
        sessions[req.session_id] = {
            "agent": SocialSyncAgent(),
            "seen_events": set()
        }
    
    session_data = sessions[req.session_id]
    agent = session_data["agent"]
    
    # 2. Add User Message
    agent.chat_history.append(HumanMessage(content=req.message))
    
    # 3. LLM Thinking
    ai_response = agent.llm.invoke(agent.chat_history)
    ai_text = ai_response.content
    
    events_to_return = []
    final_text = ai_text
    mission_complete = False

    # 4. Logic Loop
    # Check for command (case insensitive)
    if "SEARCH_ACTION" in ai_text.upper():
        
        # Extract Query
        clean_text_for_parsing = ai_text.replace("**SEARCH_ACTION:**", "SEARCH_ACTION:")
        if "SEARCH_ACTION:" in clean_text_for_parsing:
            query = clean_text_for_parsing.split("SEARCH_ACTION:")[1].strip()
        else:
            # Fallback if format is weird
            query = clean_text_for_parsing.replace("SEARCH_ACTION", "").strip()
        
        # Retrieve large batch
        raw_events = agent.retrieve_events(query)
        
        # FILTER: Exclude seen events
        new_events = []
        for raw in raw_events:
            # Create a simple hash/signature of the event to check uniqueness
            if raw not in session_data["seen_events"]:
                new_events.append(raw)
        
        # SLICE: Take top 2
        events_to_show = new_events[:2]
        
        # Mark as seen
        for ev in events_to_show:
            session_data["seen_events"].add(ev)

        # Parse for Frontend
        events_to_return = [parse_event_text(e) for e in events_to_show]
        
        # Generate Follow-up Text
        if events_to_return:
            agent.chat_history.append(AIMessage(content="SEARCH_EXECUTED"))
            
            # Contextual Prompt
            if len(session_data["seen_events"]) > 2:
                sys_msg = "SYSTEM: You just showed 2 MORE events. Briefly ask if these are better."
            else:
                sys_msg = "SYSTEM: You just showed the first 2 options. Briefly ask for thoughts."

            agent.chat_history.append(SystemMessage(content=sys_msg))
            follow_up = agent.llm.invoke(agent.chat_history)
            
            # This is the text we will show
            final_text = follow_up.content
            agent.chat_history.append(follow_up)
        else:
            # No new events found
            final_text = "I've run out of new events matching that vibe! Should we try a different category?"
            
    elif "MISSION_COMPLETE" in ai_text:
        final_text = "Mission Complete! Have a great time! 🎉"
        mission_complete = True
    else:
        # Standard chat (no search)
        agent.chat_history.append(ai_response)
        final_text = ai_text

    # --- FINAL CLEANUP ---
    # Ensure no commands leak to the frontend
    final_text = strip_command_from_text(final_text)

    return ChatResponse(
        text=final_text, 
        events=events_to_return, 
        mission_complete=mission_complete
    )

@app.post("/reset")
async def reset_chat(req: ChatRequest):
    sessions[req.session_id] = {
        "agent": SocialSyncAgent(),
        "seen_events": set()
    }
    return {"status": "reset"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)