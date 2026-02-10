import streamlit as st
import os
import requests
import time

def try_toggle_backend(active):
    """Retries backend connection for up to 60 seconds."""
    start_time = time.time()
    while time.time() - start_time < 60:
        try:
            requests.post("http://localhost:8000/toggle", json={"active": active}, timeout=5)
            return True
        except:
            time.sleep(2)
    return False

def render_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("👁️ Visionary: AI Security Agent")
        st.markdown("### *Autonomous Workplace Safety Monitor*")

def render_sidebar():
    with st.sidebar:
        st.image("https://img.icons8.com/nolan/96/artificial-intelligence.png", width=64)
        st.title("Control Center")
        st.divider()

        # Start Button Logic
        if 'started' not in st.session_state:
            try:
                # Sync with Backend State
                resp = requests.get("http://localhost:8000/status", timeout=2)
                if resp.status_code == 200:
                    st.session_state['started'] = resp.json().get("active", False)
                else:
                    st.session_state['started'] = False
            except:
                st.session_state['started'] = False

        if st.button("🚀 Start Operation"):
            with st.spinner("Connecting to Backend... (waiting for Ollama)"):
                if try_toggle_backend(True):
                    st.session_state['started'] = True
                    st.rerun()
                else:
                    st.error("❌ Backend Unreachable (Timeout 60s)")

        if st.button("🛑 Stop"):
            with st.spinner("Stopping..."):
                if try_toggle_backend(False):
                    st.session_state['started'] = False
                    st.rerun()
                else:
                    st.error("❌ Connection Failed")


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

        st.markdown("---")
        st.header("🔍 Forensic Search")
        filter_date = st.date_input("Filter by Date", value=None)
        show_violations = st.checkbox("Show Violations Only", value=False)
        
        return filter_date, show_violations

def render_metrics(df, is_active):
    m1, m2, m3 = st.columns(3)
    
    status_text = "ACTIVE" if is_active else "PAUSED"
    delta_text = "Monitoring" if is_active else "Offline"
    delta_color = "normal" if is_active else "off"
    
    with m1:
        st.metric("System Status", status_text, delta=delta_text, delta_color=delta_color)
    
    with m2:
        if is_active:
            violation_count = len(df[df['Verdict'].str.contains("VIOLATION", case=False)]) if not df.empty else 0
            st.metric("Violations Found", f"{violation_count}", delta_color="inverse")
        else:
            st.metric("Violations Found", "--")

    with m3:
        if is_active:
            last_time = df.iloc[0]['Timestamp'].split(" ")[1] if not df.empty else "--:--"
            st.metric("Last Update", last_time)
        else:
            st.metric("Last Update", "--")

def display_logs(df):
    if df.empty:
        st.warning("No data available.")
        return

    for index, row in df.iterrows():
        verdict = str(row['Verdict'])
        timestamp = row['Timestamp']
        
        if "VIOLATION" in verdict.upper():
            # Clean up text for header
            clean_verdict = verdict.replace("VIOLATION:", "").replace("Violation:", "").strip()
            header_text = f"🚨 {timestamp} | VIOLATION: {clean_verdict[:60]}..."
        else:
            header_text = f"✅ {timestamp} | No Policy Violated"
        
        with st.expander(header_text):
            # EVIDENCE DISPLAY
            if row['ImagePath']:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                # Path is relative to backend, so we need to adjust
                img_path = os.path.join(base_dir, '..', 'backend', 'evidence', row['ImagePath'])
                if os.path.exists(img_path):
                    st.image(img_path, caption="📸 Evidence Captured", width=400)
            
            st.markdown(f"**Scene Description:**\n{row['SceneDescription']}")
            st.markdown(f"**System Instruction:**\n{row['SystemInstruction']}")
            st.markdown(f"**Compliance Prompt:**\n{row['CompliancePrompt']}")
            st.divider()
            st.text(f"Raw Result: {row['Result']}")
