import streamlit as st
from pathlib import Path
import sys

# --- Add project root to Python path ---
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.auth import check_login  # ✅ removed 'init_auth'
from utils.theme import apply_theme, get_theme_css

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="Samvaad - ISL Translator",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Apply Custom Theme ---
apply_theme()
st.markdown(get_theme_css(), unsafe_allow_html=True)

# --- Main App ---
def main():
    # Hero Section
    st.markdown("""
        <div class="hero-section">
            <h1 class="main-title">🌿 Samvaad</h1>
            <p class="subtitle">A Real-Time Indian Sign Language Translator</p>
            <p class="tagline">Breaking barriers through real-time gesture and voice translation</p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- Feature Cards ---
    st.markdown("### ✨ Key Features")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">✋</div>
                <h3>Sign → Text</h3>
                <p>Real-time recognition of ISL gestures to text</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🔤</div>
                <h3>Text → Sign</h3>
                <p>Convert written text into animated sign language</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🎙️</div>
                <h3>Speech → Sign</h3>
                <p>Voice input converted to visual signs</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🗣️</div>
                <h3>Sign → Speech</h3>
                <p>Gestures converted to spoken words</p>
            </div>
        """, unsafe_allow_html=True)
    
    # --- CTA Section ---
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class="cta-section">
                <p class="cta-text">Ready to bridge communication gaps?</p>
            </div>
        """, unsafe_allow_html=True)
        
        # --- Conditional Buttons ---
        if not st.session_state.get('logged_in', False):
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🚀 Login", use_container_width=True, type="primary"):
                    st.switch_page("pages/1_login.py")
            with col_b:
                if st.button("✨ Sign Up", use_container_width=True):
                    st.switch_page("pages/2_Signup.py")
        else:
            if st.button("🎯 Go to Dashboard", use_container_width=True, type="primary"):
                st.switch_page("pages/3_Dashboard.py")
    
    # --- About Section ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
        ### 🌈 About Samvaad
        
        Samvaad is an AI-powered platform designed to promote inclusive communication 
        through Indian Sign Language (ISL). Our mission is to make communication accessible 
        to everyone, regardless of their hearing or speech abilities.
        
        **Built with:**
        - 🧠 TensorFlow & MediaPipe for gesture recognition  
        - 🎙️ Speech Recognition for voice input  
        - 🎨 Streamlit for interactive UI  
        - 💙 Empathy and accessibility in mind  
    """)
    
    # --- Footer ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📧 Contact**")
        st.markdown("support@samvaad.ai")
    
    with col2:
        st.markdown("**🔗 Links**")
        st.markdown("[GitHub](https://github.com/sindgisrishtis/Samvaad) | [Documentation](https://docs.samvaad.ai)")
    
    with col3:
        st.markdown("**💙 Credits**")
        st.markdown("Built with love for inclusive communication")

# --- Run main ---
if __name__ == "__main__":
    main()
