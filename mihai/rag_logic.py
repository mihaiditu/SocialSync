import os
import time
import textwrap
import datetime
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# --- SETUP ---
load_dotenv(dotenv_path="./.env")
DB_PATH = "./chroma_db"

import warnings
warnings.filterwarnings("ignore")

print("\n🔋 SOCIALSYNC: Powering up Agentic Core...")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7) 

print("✅ SOCIALSYNC: Online.")

class SocialSyncAgent:
    def __init__(self):
        self.llm = llm 
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        self.system_prompt = f"""
        You are SocialSync, an empathetic AI assistant for events in Bucharest.
        Today's date is: {today}.

        GOAL: Help the user find an event they LOVE.

        PHASE 1: GATHER INFO
        Ask conversational questions to determine Vibe, Time, Location, Budget.
        
        PHASE 2: SEARCH
        When you have criteria, output exactly: "SEARCH_ACTION: keywords"
        - Do NOT put the keywords in brackets [].
        - Do NOT bold the text. 
        - Example: SEARCH_ACTION: techno party weekend
        
        PHASE 3: FEEDBACK LOOP
        The system will show you the events found.
        Then you MUST ask: "Does this look good to you?"
        
        - If User says YES: Output exactly "MISSION_COMPLETE".
        - If User says NO: Ask "What should we change?".
        """
        self.chat_history = [SystemMessage(content=self.system_prompt)]

    def retrieve_events(self, search_query, k=3):
        print(f"   [DEBUG: Agent searching for: '{search_query}']")
        results = vector_db.similarity_search(f"Event: {search_query}", k=k)
        events = []
        for doc in results:
            if "Event:" in doc.page_content:
                events.append(doc.page_content)
        return events

    def run_agentic_loop(self):
        pass

if __name__ == "__main__":
    agent = SocialSyncAgent()
    print("Agent ready.")