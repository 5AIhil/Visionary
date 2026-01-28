from fastapi import FastAPI, HTTPException
from httpx import Client
from pydantic import BaseModel
import sqlite3
import uvicorn
import ollama
import base64
import io
from PIL import Image
from datetime import datetime

# 1. SETUP
app = FastAPI()

# FORCE CONNECTION TO LOCALHOST
#client = Client(host='http://127.0.0.1:11434')

# 2. DATABASE (SQLite)
def init_db():
    conn = sqlite3.connect('visionary.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY, timestamp TEXT, prompt TEXT, result TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 3. DATA MODELS
class AnalysisRequest(BaseModel):
    image_base64: str
    prompt: str

# 4. API ENDPOINT
@app.post("/analyze")
async def analyze_image(request: AnalysisRequest):
    try:
        print(f"📩 Received request: {request.prompt}")
        
        # Decode the base64 image just to verify it's valid (optional but good practice)
        try:
            image_data = base64.b64decode(request.image_base64)
            # Ollama expects the raw bytes path or bytes object. 
            # The python library handles bytes directly if passed correctly.
        except Exception as e:
            return {"status": "error", "message": "Invalid Image Data"}

        # CALL LOCAL OLLAMA 
        # Note: Ollama runs on your PC
        response = ollama.chat(
            model='llava',
            messages=[{
                'role': 'user',
                'content': request.prompt,
                'images': [image_data]
            }]
        )
        
        ai_text = response['message']['content']
        print(f"🧠 Local AI Says: {ai_text}")

        # Log to Database
        conn = sqlite3.connect('visionary.db')
        c = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO logs (timestamp, prompt, result) VALUES (?, ?, ?)", 
                  (timestamp, request.prompt, ai_text))
        conn.commit()
        conn.close()

        return {"status": "success", "ai_response": ai_text, "timestamp": timestamp}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)