from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import uvicorn
from ollama import Client
import base64
import shutil
import os
from datetime import datetime
from dotenv import load_dotenv

# MODULE IMPORTS
from rag import ingest_policy_document, check_policy_violation, generate_safety_prompt
from database import init_db, log_event
from alerts import send_telegram_alert

load_dotenv()
SYSTEM_PROMPT_FILE = "system_prompt.txt"

app = FastAPI()
client = Client(host='http://127.0.0.1:11434')

# Initialize DB on start
init_db()

# --- 2. UPLOAD ENDPOINT ---
@app.post("/upload_policy")
async def upload_policy(file: UploadFile = File(...)):
    file_location = f"temp_{file.filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    ingest_policy_document(file_location)
    
    # Generate and save dynamic prompt
    new_prompt = generate_safety_prompt(file_location)
    
    # Save to file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(BASE_DIR, SYSTEM_PROMPT_FILE)
    with open(prompt_path, "w") as f:
        f.write(new_prompt)
    
    os.remove(file_location)
    return {"status": "success", "message": "Policy learned & Safety Prompt Updated!"}

class AnalysisRequest(BaseModel):
    image_base64: str

# --- GLOBAL STATE ---
IS_ACTIVE = False  # Default to paused

class ToggleRequest(BaseModel):
    active: bool

@app.get("/status")
def get_status():
    return {"active": IS_ACTIVE}

@app.post("/toggle")
def toggle_status(request: ToggleRequest):
    global IS_ACTIVE
    IS_ACTIVE = request.active
    state = "ACTIVE" if IS_ACTIVE else "PAUSED"
    print(f"🔄 System State Updated: {state}")
    return {"status": "success", "active": IS_ACTIVE}

# --- 3. ANALYZE ENDPOINT ---
@app.post("/analyze")
async def analyze_image(request: AnalysisRequest):
    # Check if system is active
    if not IS_ACTIVE:
        return {"status": "paused", "ai_response": "Running... (Paused)"}

    print("📩 Processing Frame for Compliance...")
    ai_response_text = "Processing..." # Default value
    
    # Load dynamic prompt if available
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(BASE_DIR, SYSTEM_PROMPT_FILE)
    
    # Default fallback if no policy loaded
    system_instruction = "You are a Safety Officer. Describe the scene and identify any hazards."
    
    if os.path.exists(prompt_path):
        with open(prompt_path, "r") as f:
            # STRICT MODE: Use the generated prompt exactly as is.
            system_instruction = f.read().strip()
            
    print(f"   🤖 Using Prompt: {system_instruction[:50]}...")

    compliance_prompt_log = "N/A" # Default for logging if no rules found
    image_path_log = "" # Default empty path

    try:
        # A. SEE
        image_bytes = base64.b64decode(request.image_base64)
        desc_response = client.chat(
            model='llava-phi3',
            messages=[{'role': 'user', 'content': system_instruction, 'images': [image_bytes]}],
            options={'num_predict': 256} # Increase limit to support bounding box coordinate logic
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
            compliance_prompt_log = compliance_prompt # Store for logging
            
            judge_response = client.chat(
                model='llava-phi3', 
                messages=[{'role': 'user', 'content': compliance_prompt}],
                options={'num_predict': 128} # Optimize speed
            )
            verdict = judge_response['message']['content']
            print(f"   ⚖️ Verdict: {verdict}")

            if "VIOLATION" in verdict.upper():
                send_telegram_alert(verdict, scene_desc, relevant_rules)
                
                # --- AUTO-CAPTURE EVIDENCE ---
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"violation_{timestamp_str}.jpg"
                evidence_path = os.path.join(BASE_DIR, "evidence", filename)
                
                with open(evidence_path, "wb") as f:
                    f.write(image_bytes)
                
                print(f"   📸 Saved Evidence: {filename}")
                image_path_log = filename 
                # -----------------------------
        
        # Set final text for database
        ai_response_text = f"{verdict} | Scene: {scene_desc[:50]}..."

        # --- D. LOG TO DATABASE ---
        log_event(
            prompt_type="Compliance Check",
            result=ai_response_text,
            instruction=system_instruction,
            scene=scene_desc,
            compliance_prompt=compliance_prompt_log,
            verdict=verdict,
            image_path=image_path_log
        )
        # --------------------------

        return {"status": "success", "ai_response": verdict}

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)