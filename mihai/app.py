import streamlit as st
import time
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Import your actual backend
from rag_logic import SocialSyncAgent

st.set_page_config(page_title="SocialSync AI", page_icon="🤝", layout="wide")

# --- CUSTOM CSS FOR "CHAT BUBBLES" ---
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .event-card {
        background-color: #f0f2f6;
        border-left: 5px solid #ff4b4b;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        color: #31333F;
    }
    .event-title {
        font-weight: bold;
        font-size: 1.1em;
        color: #000;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR INFO ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/handshake.png", width=100)
    st.title("SocialSync")
    st.markdown("### The Anti-Loneliness Agent")
    st.markdown("---")
    st.info("""
    **How it works:**
    1. Chat with the AI.
    2. It learns your **Vibe**, **Schedule**, and **Budget**.
    3. It scans local events (RAG).
    4. It connects you with your tribe.
    """)
    if st.button("Reset Conversation"):
        st.session_state.agent = SocialSyncAgent()
        st.session_state.messages = []
        st.rerun()

# --- INITIALIZATION ---
# We store the AGENT OBJECT in the session state so it remembers context
if "agent" not in st.session_state:
    st.session_state.agent = SocialSyncAgent()

# We store the DISPLAY MESSAGES separately for the UI
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm SocialSync. I'm here to connect you with your tribe. Tell me, what's on your mind?"}
    ]

# --- HELPER: FORMAT EVENTS FOR UI ---
def format_event_markdown(raw_text):
    """Turns raw text into a pretty Streamlit card"""
    lines = raw_text.split('\n')
    info = {}
    for line in lines:
        if ": " in line:
            key, val = line.split(": ", 1)
            info[key.strip()] = val.strip()

    title = info.get("Event", "Unknown Event")
    date = info.get("Date", "TBD")
    loc = info.get("Location", "Check URL")
    cost = info.get("Cost", "Free")
    url = info.get("Source", "#")
    desc = info.get("Description", "")

    return f"""
    <div class="event-card">
        <div class="event-title">🏆 {title}</div>
        <p>📅 <b>When:</b> {date} | 📍 <b>Where:</b> {loc}</p>
        <p>💰 <b>Cost:</b> {cost}</p>
        <p>📝 <i>{desc}</i></p>
        <a href="{url}" target="_blank">🔗 View Event Details</a>
    </div>
    """

# --- MAIN CHAT LOOP ---
st.title("🤝 SocialSync AI")

# 1. Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("is_html"):
            st.markdown(msg["content"], unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# 2. Handle User Input
if prompt := st.chat_input("Type your answer..."):
    
    # A. Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # B. Pass to Agent Backend
    # Add to LangChain history
    st.session_state.agent.chat_history.append(HumanMessage(content=prompt))

    with st.chat_message("assistant"):
        with st.spinner("SocialSync is thinking..."):
            
            # CALL THE BRAIN
            ai_response = st.session_state.agent.llm.invoke(st.session_state.agent.chat_history)
            ai_text = ai_response.content
            
            # --- AGENT ACTION LOGIC ---
            
            # CASE 1: SEARCH ACTION
            if "SEARCH_ACTION:" in ai_text:
                search_query = ai_text.split("SEARCH_ACTION:")[1].strip()
                status_placeholder = st.empty()
                status_placeholder.info(f"🏁 Agent Decision: Searching database for '{search_query}'...")
                
                # Perform Search
                events = st.session_state.agent.retrieve_events(search_query, k=2)
                
                # Fallback
                if not events:
                    status_placeholder.warning("Broadening search criteria...")
                    events = st.session_state.agent.retrieve_events(search_query, k=50)
                    if events: events = [events[0]] # Just take top 1 if broad

                if events:
                    status_placeholder.success("Found matches!")
                    
                    # Render Events
                    for event in events:
                        card_html = format_event_markdown(event)
                        st.markdown(card_html, unsafe_allow_html=True)
                        st.session_state.messages.append({"role": "assistant", "content": card_html, "is_html": True})

                    # Inject Context back to Brain
                    st.session_state.agent.chat_history.append(AIMessage(content="SEARCH_ACTION_EXECUTED"))
                    st.session_state.agent.chat_history.append(SystemMessage(content="SYSTEM: Results shown. Ask the user if they like them."))
                    
                    # Get Follow-up Question
                    follow_up = st.session_state.agent.llm.invoke(st.session_state.agent.chat_history)
                    st.markdown(follow_up.content)
                    st.session_state.messages.append({"role": "assistant", "content": follow_up.content})
                    st.session_state.agent.chat_history.append(follow_up)
                
                else:
                    status_placeholder.error("No events found. Asking user for different preferences.")
                    st.session_state.agent.chat_history.append(SystemMessage(content="SYSTEM: No results found. Apologize and ask user to refine."))
                    follow_up = st.session_state.agent.llm.invoke(st.session_state.agent.chat_history)
                    st.markdown(follow_up.content)
                    st.session_state.messages.append({"role": "assistant", "content": follow_up.content})

            # CASE 2: MISSION COMPLETE
            elif "MISSION_COMPLETE" in ai_text:
                st.balloons()
                st.success("Mission Complete! Have fun out there! 🎉")
                st.session_state.messages.append({"role": "assistant", "content": "Mission Complete! Have fun out there! 🎉"})

            # CASE 3: NORMAL CONVERSATION
            else:
                st.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
                st.session_state.agent.chat_history.append(ai_response)