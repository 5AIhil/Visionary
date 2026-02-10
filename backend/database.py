import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'visionary.db')

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create logs table
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (Id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  Timestamp TEXT, 
                  Prompt TEXT, 
                  Result TEXT,
                  SystemInstruction TEXT, 
                  SceneDescription TEXT, 
                  CompliancePrompt TEXT, 
                  Verdict TEXT, 
                  ImagePath TEXT)''')
    
    # Ensure all columns exist (Migration logic)
    c.execute("PRAGMA table_info(logs)")
    columns = [info[1] for info in c.fetchall()]
    
    required_columns = ["SystemInstruction", "SceneDescription", "CompliancePrompt", "Verdict", "ImagePath"]
    for col in required_columns:
        if col not in columns:
            c.execute(f"ALTER TABLE logs ADD COLUMN {col} TEXT")
            
    conn.commit()
    conn.close()
    
    # Ensure evidence directory exists
    evidence_dir = os.path.join(BASE_DIR, "evidence")
    if not os.path.exists(evidence_dir):
        os.makedirs(evidence_dir)

def log_event(prompt_type, result, instruction, scene, compliance_prompt, verdict, image_path):
    conn = get_db_connection()
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    c.execute("""INSERT INTO logs 
                 (Timestamp, Prompt, Result, SystemInstruction, SceneDescription, CompliancePrompt, Verdict, ImagePath) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
              (timestamp, prompt_type, result, instruction, scene, compliance_prompt, verdict, image_path))
    
    conn.commit()
    conn.close()
