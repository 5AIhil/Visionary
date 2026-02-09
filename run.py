# to run the whole system 
import subprocess
import time
import sys
import signal
import os

# List of commands to run
commands = [
    ["ollama", "serve"],
    ["python3", "backend/backend.py"],
    ["streamlit", "run", "frontend/dash.py"],
    ["python3", "frontend/camera.py"]
]

procs = []

def cleanup(signum, frame):
    print("\n🛑 Shutting down all services...")
    for p in procs:
        p.terminate()
    sys.exit(0)

# Catch Ctrl+C
signal.signal(signal.SIGINT, cleanup)

print("🚀 Launching System...")

try:
    for cmd in commands:
        print(f"pwning: {' '.join(cmd)}")
        # Start process and store reference
        p = subprocess.Popen(cmd)
        procs.append(p)
        # Optional: stagger start times to prevent race conditions
        time.sleep(2) 

    # Keep the main script alive
    while True:
        time.sleep(1)

except Exception as e:
    cleanup(None, None)