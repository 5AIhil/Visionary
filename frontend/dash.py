import streamlit as st
import sqlite3
import pandas as pd
import requests
import time
import os

# CONFIG
st.set_page_config(page_title="Visionary Command Center", layout="wide")
API_URL = "http://localhost:8000/update_prompt"

# FUNCTIONS
def get_logs():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, '..', 'backend', 'visionary.db')
    conn = sqlite3.connect(db_path)
    # Fetch last 10 entries, newest first
    df = pd.read_sql_query("SELECT timestamp, prompt, result FROM logs ORDER BY id DESC LIMIT 10", conn)
    conn.close()
    return df

def update_prompt(new_text):
    try:
        requests.post(API_URL, json={"new_prompt": new_text})
        st.success(f"✅ Protocol Updated: Agent is now looking for '{new_text}'")
    except:
        st.error("❌ Could not connect to Backend.")

# UI LAYOUT
st.title("👁️ Visionary: AI Security Agent")

# Sidebar: Controls
with st.sidebar:

     # Start Button Logic
    if 'started' not in st.session_state:
        st.session_state['started'] = False

    if st.button("🚀 Start Operation"):
        st.session_state['started'] = True
        st.rerun()

    if st.button("🛑 Stop"):
        st.session_state['started'] = False
        st.rerun()


    st.header("⚙️ Control Panel")
    current_instruction = st.text_area("System Instruction", "Describe this image.")
    if st.button("Update Agent Task"):
        update_prompt(current_instruction)
    
    st.info("💡 **Tip:** Try prompts like:\n- 'Is there a person wearing glasses?'\n- 'Is there a fire hazard?'\n- 'Describe the emotion of the person.'")


    st.markdown("---")
    st.header("📂 Policy Manager")
    uploaded_file = st.file_uploader("Upload Safety Manual (PDF)", type="pdf")

    if uploaded_file is not None:
        if st.button("Ingest Policy"):
            with st.spinner("Embedding knowledge..."):
                files = {"file": uploaded_file.getvalue()}
                # Send file to Backend
                try:
                    response = requests.post("http://localhost:8000/upload_policy", 
                                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")})
                    if response.status_code == 200:
                        st.success("✅ Policy Rules Ingested!")
                except:
                    st.error("Backend Connection Failed")


# Main Area: Live Intel
st.subheader("📡 Live Intelligence Feed")

# Auto-refresh logic
placeholder = st.empty()

if st.session_state['started']:
    # Loop to simulate real-time updates
    # Using a while loop with a placeholder for better control than a fixed range
    while st.session_state['started']:
        df = get_logs()
        
        with placeholder.container():
            # Display key metrics
            if not df.empty:
                latest_alert = df.iloc[0]['result']
                st.metric(label="Latest Insight", value=latest_alert)
                
                st.markdown("### Incident History")
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Waiting for data from Camera Agent...")

        time.sleep(2)
else:
    st.info("Paused. Click **Start Operation** to begin monitoring.")