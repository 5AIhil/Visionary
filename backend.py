from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import uvicorn
from ollama import Client
import base64
import shutil
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import requests

# IMPORT THE NEW RAG ENGINE
from rag import ingest_policy_document, check_policy_violation

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

app = FastAPI()
client = Client(host='http://127.0.0.1:11434')

# --- 1. DATABASE SETUP (RESTORED) ---
def init_db():
    conn = sqlite3.connect('visionary.db')
    c = conn.cursor()
    # Create table for logs so Dashboard doesn't crash
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, prompt TEXT, result TEXT)''')
    conn.commit()
    conn.close()

init_db()  # <--- Run this immediately on start

# --- 2. UPLOAD ENDPOINT ---
@app.post("/upload_policy")
async def upload_policy(file: UploadFile = File(...)):
    file_location = f"temp_{file.filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    ingest_policy_document(file_location)
    
    os.remove(file_location)
    return {"status": "success", "message": "Policy learned successfully!"}

class AnalysisRequest(BaseModel):
    image_base64: str

def send_telegram_alert(violation_text, rule_broken):
    if not TELEGRAM_TOKEN: return
    msg = f"🚨 COMPLIANCE ALERT!\n\n👀 Observed: {violation_text}\n\n📜 Rule Violated: {rule_broken[:200]}..."
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                  json={"chat_id": TELEGRAM_CHAT_ID, "text": msg})

# --- 3. ANALYZE ENDPOINT (UPDATED TO LOG) ---
@app.post("/analyze")
async def analyze_image(request: AnalysisRequest):
    print("📩 Processing Frame for Compliance...")
    ai_response_text = "Processing..." # Default value
    
    try:
        # A. SEE
        image_bytes = base64.b64decode(request.image_base64)
        desc_response = client.chat(
            model='llava-phi3',
            messages=[{'role': 'user', 'content': "Describe this scene in detail. List safety gear worn or missing.", 'images': [image_bytes]}]
        )
        scene_desc = desc_response['message']['content']
        print(f"   👁️ Scene: {scene_desc}")

        # B. RETRIEVE
        relevant_rules, _ = check_policy_violation(scene_desc)
        
        # C. JUDGE
        verdict = "Compliant" # Default verdict
        if relevant_rules:
            compliance_prompt = f"""
            SCENE: {scene_desc}
            OFFICIAL POLICY: {relevant_rules}
            TASK: Does the scene violate the policy? If YES, output "VIOLATION: [Reason]". If NO, output "COMPLIANT".
            """
            
            judge_response = client.chat(
                model='llava-phi3', 
                messages=[{'role': 'user', 'content': compliance_prompt}]
            )
            verdict = judge_response['message']['content']
            print(f"   ⚖️ Verdict: {verdict}")

            if "VIOLATION" in verdict.upper():
                send_telegram_alert(scene_desc, relevant_rules)
        
        # Set final text for database
        ai_response_text = f"{verdict} | Scene: {scene_desc[:50]}..."

        # --- D. LOG TO DATABASE (CRITICAL RESTORED STEP) ---
        conn = sqlite3.connect('visionary.db')
        c = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # We log the prompt as "RAG Check" so the dashboard knows what happened
        c.execute("INSERT INTO logs (timestamp, prompt, result) VALUES (?, ?, ?)", 
                  (timestamp, "Compliance Check", ai_response_text))
        conn.commit()
        conn.close()
        # ---------------------------------------------------

        return {"status": "success", "ai_response": verdict}

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)