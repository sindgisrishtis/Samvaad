import streamlit as st

def apply_theme():
    st.markdown("""
        <style>
        body {
            background: linear-gradient(to bottom, #e6f2f8, #ffffff);
            color: #333333;
            font-family: 'Poppins', sans-serif;
        }
        .main-title { font-size: 3em; text-align: center; color: #2b6ca3; }
        .tagline { text-align: center; font-size: 1.2em; color: #555; }
        .info-card, .feature-card, .metric-card {
            background: white; border-radius: 10px; padding: 20px; 
            box-shadow: 0px 4px 8px rgba(0,0,0,0.1); text-align: center;
        }
        .metric-value { font-size: 2em; font-weight: bold; color: #2b6ca3; }
        .metric-label { font-size: 1em; color: #777; }
        .stButton>button { border-radius: 10px; font-size: 1em; padding: 10px; }
        </style>
    """, unsafe_allow_html=True)

def get_theme_css():
    return """
        <style>
        .hero-section { text-align: center; padding: 2em 0; }
        .main-title { font-size: 3em; color: #2b6ca3; }
        .tagline { font-size: 1.2em; color: #555; }
        </style>
    """

def show_success(msg):
    st.success(f"✅ {msg}")

def show_error(msg):
    st.error(f"❌ {msg}")
