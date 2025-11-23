import streamlit as st
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.auth import register_user
from utils.theme import apply_theme, get_theme_css, show_success, show_error

st.set_page_config(page_title="Signup - Samvaad", page_icon="📝", layout="centered")

apply_theme()
st.markdown(get_theme_css(), unsafe_allow_html=True)

st.markdown("""
    <div class="hero-section">
        <h1 class="main-title">📝 Create Account</h1>
        <p class="tagline">Join Samvaad and start communicating without barriers</p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    
    with st.form("signup_form"):
        st.markdown("### 🌿 Sign Up")
        
        name = st.text_input("Full Name", placeholder="Enter your name")
        email = st.text_input("Email", placeholder="Enter your email")
        username = st.text_input("Username", placeholder="Choose a username")
        password = st.text_input("Password", type="password", placeholder="Create a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
        
        signup_button = st.form_submit_button("✨ Sign Up", use_container_width=True, type="primary")
        
        if signup_button:
            if not all([name, email, username, password, confirm_password]):
                show_error("Please fill in all fields")
            elif password != confirm_password:
                show_error("Passwords do not match")
            else:
                success, message = register_user(name, email, username, password)
                if success:
                    show_success(message)
                    st.success("✅ Account created successfully! You can now log in.")
                    st.balloons()
                    st.switch_page("pages/1_Login.py")
                else:
                    show_error(message)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Already have an account?**")
    if st.button("🚀 Login Here", use_container_width=True):
        st.switch_page("pages/1_Login.py")
