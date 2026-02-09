import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# CONFIG
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "chroma_db")
EMBED_MODEL = "nomic-embed-text"

# 1. INITIALIZE VECTOR DB
def get_vector_db():
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    return Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

# 2. INGEST PDF (The "Learning" Phase)
def ingest_policy_document(file_path):
    print(f"📚 Reading Policy: {file_path}")
    
    # Load and Split PDF
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    
    # Store in Vector DB
    db = get_vector_db()
    db.add_documents(chunks)
    print(f"✅ Ingested {len(chunks)} rules into the Knowledge Base.")

# 3. CHECK FOR VIOLATIONS (The "Judge" Phase)
def check_policy_violation(scene_description):
    db = get_vector_db()
    
    # Retrieve top 3 most relevant rules for this scene
    results = db.similarity_search(scene_description, k=3)
    
    if not results:
        return None, "No relevant policies found."

    # Combine rules into a single text block
    retrieved_context = "\n".join([doc.page_content for doc in results])
    return retrieved_context, results