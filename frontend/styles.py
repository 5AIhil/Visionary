import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        .stMetric {
            background-color: #262730;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            font-weight: bold;
        }
        h1, h2, h3 {
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 600;
        }
        .block-container {
            padding-top: 2rem;
        }
        div[data-testid="stExpander"] div[role="button"] p {
            font-size: 1.1rem;
            font-weight: 500;
        }
        /* Status Indicators */
        .status-active { color: #00FF99; font-weight: bold; }
        .status-inactive { color: #FF4B4B; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)
