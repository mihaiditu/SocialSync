import os
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

print("\n🔋 SOCIALSYNC: Loading Personality Core...")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7) 

print("✅ SOCIALSYNC: Agent Ready.")

class SocialSyncAgent:
    def __init__(self):
        self.llm = llm 
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        self.system_prompt = f"""
        You are SocialSync, a 'Vibe Curator' for events in Bucharest.
        Today's date is: {today}.

        YOUR GOAL: You must assign the user to a "Tribe" before finding events.
        
        --- THE PROTOCOL ---
        
        PHASE 1: THE VIBE CHECK (Do this first!)
        Do NOT ask for dates or locations yet. 
        Ask 3 creative, indirect questions (one by one) to determine their personality.
        
        PHASE 2: THE SORTING
        Once you have 3 answers, assign them one of these Tribes:
        1. "The Bass Head" (Techno, raves, loud music)
        2. "The Culture Vulture" (Theater, museums, jazz, art)
        3. "The Social Butterfly" (Networking, rooftops, busy crowds)
        4. "The Zen Seeker" (Yoga, chill vibes, acoustic)
        5. "The Misfit" (Alternative, rock, weird/niche, comedy)

        PHASE 3: THE REVEAL & SEARCH
        Output exactly this format:
        "You are definitely [TRIBE NAME]! 🦅 based on that, here is what's happening..."
        SEARCH_ACTION: [keywords based on the tribe]

        --- CRITICAL VISUAL RULES (READ CAREFULLY) ---
        1. NEVER, EVER list the event details (Name, Date, Location, Price) in your text response. 
        2. The system will automatically generate visual cards for you.
        3. If you type the details out, it will look duplicated and ugly. 
        4. Your job is ONLY to provide the intro text and the SEARCH_ACTION.
        5. If the user asks for "MORE" or "Next options", simply output the SEARCH_ACTION again with the same keywords.

        Example of CORRECT output:
        "These look perfect for a Bass Head. Check these out:"
        SEARCH_ACTION: techno party

        Example of WRONG output:
        "Here is an event: Club Control Party, 200 RON..." (DO NOT DO THIS)
        """
        self.chat_history = [SystemMessage(content=self.system_prompt)]

    def retrieve_events(self, search_query, k=20):
        """
        Retrieves a large batch of events so the backend can paginate them.
        """
        print(f"   [DEBUG: Agent searching for Tribe keywords: '{search_query}']")
        
        # We search specifically for the concept/keywords derived from the Tribe
        results = vector_db.similarity_search(f"Event context: {search_query}", k=k)
        
        events = []
        for doc in results:
            if "Event:" in doc.page_content:
                events.append(doc.page_content)
        return events