import streamlit as st
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.auth import login_user, check_login
from utils.theme import apply_theme, get_theme_css, show_success, show_error

st.set_page_config(page_title="Login - Samvaad", page_icon="🔐", layout="centered")

apply_theme()
st.markdown(get_theme_css(), unsafe_allow_html=True)

# Redirect if already logged in
if check_login():
    st.switch_page("pages/3_Dashboard.py")

st.markdown("""
    <div class="hero-section">
        <h1 class="main-title">🔐 Welcome Back</h1>
        <p class="tagline">Login to continue your communication journey</p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.markdown("### 🌿 Login to Samvaad")
        
        username_or_email = st.text_input("Username or Email", placeholder="Enter your username or email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        remember_me = st.checkbox("Remember me")
        
        col_a, col_b = st.columns(2)
        with col_a:
            login_button = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
        with col_b:
            forgot_password = st.form_submit_button("Forgot Password?", use_container_width=True)
        
        if login_button:
            if not username_or_email or not password:
                show_error("Please fill in all fields")
            else:
                success, message = login_user(username_or_email, password)
                if success:
                    show_success(message)
                    st.balloons()
                    st.rerun()
                else:
                    show_error(message)
        
        if forgot_password:
            st.info("🔑 Password reset feature coming soon! Please contact support@samvaad.ai")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Don't have an account?**")
    if st.button("✨ Sign Up Here", use_container_width=True):
        st.switch_page("pages/2_Signup.py")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("app.py")