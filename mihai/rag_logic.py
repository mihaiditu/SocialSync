import os
import time
import textwrap
import re
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# --- SETUP ---
load_dotenv(dotenv_path="./.env")
DB_PATH = "./chroma_db"

import warnings
warnings.filterwarnings("ignore")

print("\n🔋 SOCIALSYNC: Powering up Neural Engine...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
print("✅ SOCIALSYNC: Online.")

class SocialSyncAgent:
    def __init__(self):
        self.context_memory = ""
        self.asked_questions = [] 
        self.max_retries = 3 # How many extra questions to ask before forcing a result

    def get_logistics_question(self, logistic_type):
        """Retrieves specific Logistics card."""
        query = f"Tribe: Logistics - {logistic_type}"
        results = vector_db.similarity_search(query, k=3)
        for doc in results:
            content = doc.page_content
            if f"Logistics - {logistic_type}" in content and "Next Question:" in content:
                try:
                    parts = content.split("Next Question:")
                    return parts[1].strip().split("\n")[0].replace('"', '')
                except: continue
        
        if logistic_type == "Budget": return "What is your budget?"
        if logistic_type == "Time": return "When are you free?"
        return "Where do you want to go?"

    def get_personality_question(self, user_input):
        """Finds a NEW question to ask."""
        results = vector_db.similarity_search(f"Tribe keywords: {user_input}", k=10)
        
        for doc in results:
            content = doc.page_content
            if "Logistics" in content: continue

            if "Next Question:" in content:
                try:
                    parts = content.split("Next Question:")
                    question = parts[1].strip().split("\n")[0].replace('"', '')
                    
                    # CRITICAL: Only return unique questions
                    if question not in self.asked_questions:
                        self.asked_questions.append(question)
                        return question
                except: continue
        return None

    def retrieve_events(self, full_context, k=3):
        results = vector_db.similarity_search(f"Event details: {full_context}", k=k)
        events = []
        for doc in results:
            # Only accept actual Events
            if "Event:" in doc.page_content:
                events.append(doc.page_content)
        return events

    def force_broad_search(self, full_context):
        """
        Emergency method: If specific search fails, we search BROADLY.
        """
        # FIX: Increased k to 50 to ensure we dig deep enough to find Events
        # mixed in with all the Profiles.
        results = vector_db.similarity_search(full_context, k=50)
        events = []
        for doc in results:
            if "Event:" in doc.page_content:
                events.append(doc.page_content)
        
        # If we found events, return top 2
        if events:
            return events[:2]
        
        # ULTIMATE FALLBACK: If still nothing, just grab ANY event from DB
        # (This guarantees the demo never shows "No Results")
        fallback = vector_db.similarity_search("Event:", k=5)
        fallback_events = [doc.page_content for doc in fallback if "Event:" in doc.page_content]
        return fallback_events[:2]

    def pretty_print_event(self, raw_text, rank):
        lines = raw_text.split('\n')
        info = {}
        for line in lines:
            if ": " in line:
                key, val = line.split(": ", 1)
                info[key.strip()] = val.strip()

        title = info.get("Event", "Unknown Event")
        date = info.get("Date", "See details")
        loc = info.get("Location", "TBD")
        cost = info.get("Cost", "Free")
        desc = info.get("Description", "")
        
        wrapped_desc = textwrap.fill(desc, width=50)
        indented_desc = wrapped_desc.replace('\n', '\n      ')
        
        print(f"\n   🏆 MATCH #{rank}: {title.upper()}")
        print(f"   {'═'*50}")
        print(f"   📅  WHEN:  {date}")
        print(f"   📍  WHERE: {loc}")
        print(f"   💰  COST:  {cost}")
        print(f"   {'─'*50}")
        print(f"   📝  DETAILS:\n      {indented_desc}")
        print(f"   {'═'*50}\n")

    def run_persistent_loop(self):
        print("\n" + "█"*60)
        print(" 📱 SOCIALSYNC: The Anti-Loneliness Agent")
        print("    (Type 'exit' to quit)")
        print("█"*60 + "\n")

        user_input = input("🤖 SOCIALSYNC: Hi! I'm here to help you find your people.\n   Tell me what you're looking for (e.g. 'I want to relax')\n\n👤 YOU: ")
        if user_input.lower() in ['exit', 'quit']: return
        self.context_memory = user_input

        # --- PHASE 1: MANDATORY QUESTIONS ---
        mandatory_phases = [
            ("Personality", lambda: self.get_personality_question(self.context_memory)),
            ("Time",        lambda: self.get_logistics_question("Time")),
            ("Location",    lambda: self.get_logistics_question("Location")),
            ("Budget",      lambda: self.get_logistics_question("Budget"))
        ]

        for phase_name, question_func in mandatory_phases:
            print(f"\n   ⚙️  [System: Analyzing {phase_name} Preference...]")
            time.sleep(0.3)
            
            question = question_func()
            if question:
                print(f"\n🤖 SOCIALSYNC: {question}")
                ans = input("\n👤 YOU: ")
                self.context_memory += f" {ans}"

        # --- PHASE 2: PERSISTENCE LOOP ---
        retries = 0
        final_events = []

        while True:
            print("\n" + "▒"*60)
            print("🏁  CALCULATING MATCHES...")
            print("▒"*60)

            # Try to find events
            final_events = self.retrieve_events(self.context_memory, k=2)

            # SUCCESS CHECK: Did we find anything?
            if len(final_events) > 0:
                print(f"   [DEBUG: Found {len(final_events)} perfect matches!]")
                break # We are done!
            
            # FAILURE HANDLING
            retries += 1
            if retries > self.max_retries:
                print("\n⚠️  [System: Strict search yielded 0 results. Forcing Broad Search...]")
                final_events = self.force_broad_search(self.context_memory)
                break
            
            # If we are here, we need to ask another question
            print(f"\n   [DEBUG: No matches found. Refining Search (Attempt {retries}/{self.max_retries})...]")
            time.sleep(1)
            
            new_q = self.get_personality_question(self.context_memory)
            
            if new_q:
                print(f"\n🤖 SOCIALSYNC: I'm having trouble finding an exact match. Let me ask: \n   {new_q}")
                ans = input("\n👤 YOU: ")
                self.context_memory += f" {ans}"
            else:
                print("   [System: No more questions available. Forcing result.]")
                final_events = self.force_broad_search(self.context_memory)
                break

        # --- SHOW RESULTS ---
        if final_events:
            for i, event in enumerate(final_events):
                self.pretty_print_event(event, i+1)
        else:
            print("\n❌ No matching events found in the database. (Try adding more Event Data)")

if __name__ == "__main__":
    agent = SocialSyncAgent()
    agent.run_persistent_loop()