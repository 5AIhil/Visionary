import os
import requests
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(verdict, scene_desc, rule_broken):
    if not TELEGRAM_TOKEN: 
        return
        
    # Format: Alert -> Verdict -> Rule
    msg = f"🚨 COMPLIANCE ALERT!\n\n📜 Policy: {rule_broken[:300]}\n\n❌ {verdict}..."
    
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      json={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    except Exception as e:
        print(f"⚠️ Failed to send Telegram alert: {e}")
