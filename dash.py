import streamlit as st
import sqlite3
import pandas as pd
import requests
import time

# CONFIG
st.set_page_config(page_title="Visionary Command Center", layout="wide")
API_URL = "http://localhost:8000/update_prompt"

# FUNCTIONS
def get_logs():
    conn = sqlite3.connect('visionary.db')
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

    st.header("⚙️ Control Panel")
    current_instruction = st.text_area("System Instruction", "Describe this image.")
    if st.button("Update Agent Task"):
        update_prompt(current_instruction)
    
    st.info("💡 **Tip:** Try prompts like:\n- 'Is there a person wearing glasses?'\n- 'Is there a fire hazard?'\n- 'Describe the emotion of the person.'")


# Main Area: Live Intel
st.subheader("📡 Live Intelligence Feed")

# Auto-refresh logic
placeholder = st.empty()

# Loop to simulate real-time updates (Streamlit refreshes on interaction, but this helps)
for seconds in range(200):
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