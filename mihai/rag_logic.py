import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
# CHANGE: Using Local CPU Embeddings
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv(dotenv_path="./.env")
DB_PATH = "./chroma_db"

# Initialize with the same Local Model
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

def get_relevant_context(query_text, k=3):
    print(f"🔍 Local RAG Search for: '{query_text}'...")
    
    results = vector_db.similarity_search(query_text, k=k)
    
    context_string = ""
    for i, doc in enumerate(results):
        context_string += f"\n--- INFO {i+1} ---\n{doc.page_content}\n"
    
    return context_string

if __name__ == "__main__":
    try:
        print(get_relevant_context("Where is the hiking group meeting?"))
    except Exception as e:
        print(f"Error: {e}")