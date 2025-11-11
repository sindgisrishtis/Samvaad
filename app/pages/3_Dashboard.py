import streamlit as st
import sys
from pathlib import Path

# Setup path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.auth import check_login, logout_user, get_user_info
from utils.theme import apply_theme, get_theme_css

# Page config
st.set_page_config(page_title="Dashboard - Samvaad", page_icon="🏠", layout="wide")

# Apply theme
apply_theme()
st.markdown(get_theme_css(), unsafe_allow_html=True)

# Redirect if not logged in
if not check_login():
    st.warning("⚠️ Please login first")
    st.switch_page("pages/1_🔐_Login.py")

user_info = get_user_info()
username = user_info.get("username", "User") if user_info else "User"

# Sidebar
with st.sidebar:
    st.markdown(f"### 👋 Welcome, {username}")
    st.markdown("#### 📂 Navigation")
    st.markdown("---")

    if st.button("✋ Sign → Text", use_container_width=True):
        st.switch_page("pages/4_Sign_to_Text.py")

    if st.button("🎙️ Sign → Speech", use_container_width=True):
        st.switch_page("pages/5_Sign_to_Speech.py")

    if st.button("🔤 Text → Sign", use_container_width=True):
        st.switch_page("pages/6_Text_to_Sign.py")

    if st.button("🗣️ Speech → Sign", use_container_width=True):
        st.switch_page("pages/7_Speech_to_Sign.py")

    if st.button("📊 Analytics", use_container_width=True):
        st.switch_page("pages/8_Analytics.py")

    if st.button("🎯 Practice Mode", use_container_width=True):
        st.switch_page("pages/9_Practice.py")

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        logout_user()
        st.success("You’ve been logged out successfully.")
        st.switch_page("app.py")

# Main UI
st.markdown("""
    <div class="hero-section">
        <h1 class="main-title">🏠 Dashboard</h1>
        <p class="tagline">Your central hub for all Samvaad translation features</p>
    </div>
""", unsafe_allow_html=True)

# Dashboard cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">✋</div>
            <h3>Sign → Text</h3>
            <p>Recognize ISL gestures and convert them to text instantly.</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔤</div>
            <h3>Text → Sign</h3>
            <p>Translate text to sign animations and learn visually.</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🗣️</div>
            <h3>Speech → Sign</h3>
            <p>Speak and see your words translated into ISL signs.</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Analytics</h3>
            <p>Track your translation accuracy and performance over time.</p>
        </div>
    """, unsafe_allow_html=True)

# CTA buttons
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

colA, colB, colC = st.columns([1, 2, 1])
with colB:
    st.markdown("""
        <div class="cta-section">
            <h3>🚀 Choose a mode to get started!</h3>
        </div>
    """, unsafe_allow_html=True)

    st.button("✋ Start Sign → Text", use_container_width=True, key="sign_text", on_click=lambda: st.switch_page("pages/4_Sign_to_Text.py"))
    st.button("🔤 Start Text → Sign", use_container_width=True, key="text_sign", on_click=lambda: st.switch_page("pages/6_Text_to_Sign.py"))
    st.button("🎙️ Start Speech → Sign", use_container_width=True, key="speech_sign", on_click=lambda: st.switch_page("pages/7_Speech_to_Sign.py"))
    st.button("📊 View Analytics", use_container_width=True, key="analytics", on_click=lambda: st.switch_page("pages/8_📊_Analytics.py"))
