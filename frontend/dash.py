import streamlit as st
import sqlite3
import pandas as pd
import requests
import time
import os

# MODULE IMPORTS
from styles import apply_custom_css
from components import render_header, render_sidebar, render_metrics, display_logs

# CONFIG
st.set_page_config(page_title="Visionary Command Center", layout="wide", page_icon="👁️")
apply_custom_css()

# API CONFIG
API_URL = "http://localhost:8000/update_prompt"

# DATA FETCHING
def get_logs(date_filter=None, violation_only=False):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, '..', 'backend', 'visionary.db')
    conn = sqlite3.connect(db_path)
    
    query = "SELECT Id, Timestamp, Prompt, Result, SystemInstruction, SceneDescription, CompliancePrompt, Verdict, ImagePath FROM logs WHERE 1=1"
    params = []
    
    if date_filter:
        query += " AND date(Timestamp) = ?"
        params.append(str(date_filter))
        
    if violation_only:
        query += " AND Verdict LIKE '%VIOLATION%'"
    
    query += " ORDER BY Id DESC"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# UI LAYOUT
render_header()
filter_date, show_violations = render_sidebar()

# MAIN FEED
st.subheader("📡 Live Intelligence Feed")
main_placeholder = st.empty()

if st.session_state.get('started', False):
    while st.session_state['started']:
        df = get_logs(date_filter=filter_date, violation_only=show_violations)
        
        with main_placeholder.container():
            st.markdown("---")
            render_metrics(df, is_active=True)
            
            st.markdown("### 📡 Live Feed")
            if not df.empty:
                display_logs(df)
            else:
                st.info("Waiting for data from Camera Agent...")
        
        time.sleep(2)

else:
    with main_placeholder.container():
        st.markdown("---")
        # For paused state, we pass an empty DF or handle it in render_metrics
        df = get_logs(date_filter=filter_date, violation_only=show_violations)
        render_metrics(df, is_active=False)
        
        st.markdown("### 📡 Live Feed (Paused)")
        if not df.empty:
            display_logs(df)