import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# CONFIG
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "chroma_db")
EMBED_MODEL = "nomic-embed-text"

# 1. INITIALIZE VECTOR DB (Persistent Global Connection)
print("🔌 Initializing Vector Database connection...")
_embeddings = OllamaEmbeddings(model=EMBED_MODEL)
_db_instance = Chroma(persist_directory=DB_PATH, embedding_function=_embeddings)

def get_vector_db():
    return _db_instance

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

# 4. GENERATE SYSTEM PROMPT (The "Teacher" Phase)
from ollama import Client

def generate_safety_prompt(file_path):
    print(f"🧠 Generating Safety Prompt from: {file_path}")
    
    # Load PDF text
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    full_text = "\n".join([doc.page_content for doc in docs])
    
    # Truncate if too long (approx 10k chars to fit context)
    if len(full_text) > 10000:
        full_text = full_text[:10000] + "...(truncated)"

    client = Client(host='http://127.0.0.1:11434')
    
    instruction = f"""
    You are an expert Security Consultant.
    
    ACTION: Read the safety policy below and write a "System Instruction" for a Computer Vision AI.
    
    The System Instruction must:
    1. Define the AI's role: "You are a Safety Compliance Officer responsible for..."
    2. List the specific rules it must enforce based on the text.
    3. Instruct the AI to explicitly use spatial reasoning. Tell it to output findings using bounding box layouts in the format [x_min, y_min, x_max, y_max] or use relative position markers (e.g. 'Subject at [top-left] is too close to the hazard at [bottom-right]') to accurately map metrics.
    4. Be strict and direct.
    
    OUTPUT FORMAT:
    "You are a Safety Compliance Officer. Your task is to monitor the feed for [Key Hazards]. You must flag [Specific Violations]. If you see [Safe Behavior], mark it as compliant. Always describe locations using explicit bounding box coordinates [x1, y1, x2, y2] to identify actors and threats precisely."
    
    POLICY CONTENT:
    {full_text}
    """
    
    response = client.chat(
        model='llava-phi3',
        messages=[{'role': 'user', 'content': instruction}]
    )
    
    generated_prompt = response['message']['content']
    print(f"✨ Generated Prompt: {generated_prompt}")
    return generated_prompt