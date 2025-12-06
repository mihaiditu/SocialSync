import os
import shutil
import re
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

load_dotenv(dotenv_path="./.env")
DATA_PATH = "./data_raw"
DB_PATH = "./chroma_db"

def ingest_data():
    print("🔄 SOCIALSYNC: Re-indexing Memory (Dual Mode)...")

    # 1. Clear old database
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)

    documents = []
    
    # 2. Iterate through all files in data_raw
    for filename in os.listdir(DATA_PATH):
        file_path = os.path.join(DATA_PATH, filename)
        
        # Skip system files
        if not filename.endswith(".txt"): continue

        print(f"   📂 Processing: {filename}...")
        
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        # MODE A: PROFILES (Regex Split)
        if "profiles" in filename:
            raw_chunks = re.split(r'(?=Tribe:)', raw_text)
            for chunk in raw_chunks:
                if "Tribe:" in chunk and "Next Question:" in chunk:
                    documents.append(Document(page_content=chunk.strip(), metadata={"source": "profile"}))
            print(f"     -> Extracted {len(raw_chunks)} profiles.")

        # MODE B: EVENTS (Standard Split)
        else:
            # Split by dashed line
            raw_chunks = raw_text.split("------------------------------------------------")
            for chunk in raw_chunks:
                if "Event:" in chunk:
                    documents.append(Document(page_content=chunk.strip(), metadata={"source": "event"}))
            print(f"     -> Extracted {len(raw_chunks)} events.")

    # 3. Save to Vector DB
    if not documents:
        print("❌ Error: No valid data found.")
        return

    print(f"💾 Saving {len(documents)} total memories to Database...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    Chroma.from_documents(
        documents=documents, 
        embedding=embeddings, 
        persist_directory=DB_PATH
    )
    
    print("✅ SOCIALSYNC: Indexing Complete.")

if __name__ == "__main__":
    ingest_data()