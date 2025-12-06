import os
import shutil
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# CHANGE: Using Local CPU Embeddings (Free & Unlimited)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv(dotenv_path="./.env")

DATA_PATH = "./data_raw"
DB_PATH = "./chroma_db"

def ingest_data():
    print("🔄 Starting data ingestion (Local CPU Powered)...")

    # Clear old DB to prevent conflicts between Google/Local vectors
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
        print("🧹 Cleared old database format.")

    # Load Docs
    loader = DirectoryLoader(DATA_PATH, glob="./*.txt", loader_cls=TextLoader)
    documents = loader.load()
    
    if not documents:
        print("⚠️ No documents found. Add .txt files to 'data_raw'.")
        return

    # Split Text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    print(f"🧩 Split into {len(chunks)} chunks.")

    # Create DB using Local Model
    print("💾 Downloading model and saving embeddings locally...")
    print("   (The first time runs slower because it downloads the model)")
    
    # This uses a small, fast model directly on your laptop
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=DB_PATH
    )
    
    print("✅ Success! Database created locally. No API limits!")

if __name__ == "__main__":
    ingest_data()