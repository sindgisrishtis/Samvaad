import streamlit as st
import sys
from pathlib import Path
import cv2
import numpy as np
import pyttsx3
from PIL import Image

# Setup paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.model_handler import get_model_handler
from utils.auth import check_login
from utils.theme import apply_theme, get_theme_css

# Streamlit page settings
st.set_page_config(page_title="Sign → Speech - Samvaad", page_icon="🖐️", layout="wide")

# Apply custom theme
apply_theme()
st.markdown(get_theme_css(), unsafe_allow_html=True)

# Redirect if user not logged in
if not check_login():
    st.warning("⚠️ Please login to use the translator.")
    st.switch_page("pages/1_login.py")

# Load model handler
model_handler = get_model_handler()

# Initialize Text-to-Speech engine
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 170)
tts_engine.setProperty("volume", 1.0)

# --- Title ---
st.markdown("""
    <div class="hero-section">
        <h1 class="main-title">🖐️ Sign → Speech Translator</h1>
        <p class="tagline">Show your sign or upload an image — Samvaad will recognize it and speak it aloud!</p>
    </div>
""", unsafe_allow_html=True)

# Choose input method
mode = st.radio("Choose input method:", ["📷 Live Camera", "📤 Upload Image"])
sentence_mode = st.checkbox("🗣️ Sentence Mode (append letters to form words)")
st.markdown("---")

# Store recognized text
if "spoken_text" not in st.session_state:
    st.session_state.spoken_text = ""

# =======================
# 📷 Live Camera Mode
# =======================
if mode == "📷 Live Camera":
    st.info("🎥 Allow camera access and show your ISL sign clearly.")

    run = st.checkbox("Start Webcam")

    if run:
        frame_placeholder = st.empty()
        prediction_placeholder = st.empty()

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("🚫 Unable to access camera. Please check permissions.")
        else:
            last_label = ""
            while run:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to read from webcam.")
                    break

                frame = cv2.flip(frame, 1)
                frame = cv2.resize(frame, (640, 480))
                frame = cv2.convertScaleAbs(frame, alpha=1.3, beta=25)

                # Extract landmarks
                landmarks, hand_landmarks = model_handler.extract_landmarks(frame)

                if landmarks is not None:
                    label, confidence = model_handler.predict_sign(landmarks)
                    frame = model_handler.draw_landmarks(frame, hand_landmarks)

                    if label:
                        prediction_placeholder.markdown(
                            f"### 🧠 Prediction: **{label}** ({confidence:.1%} confidence)"
                        )

                        # Build sentence or replace single letter
                        if sentence_mode:
                            if len(st.session_state.spoken_text) == 0 or label != st.session_state.spoken_text[-1]:
                                st.session_state.spoken_text += label
                        else:
                            st.session_state.spoken_text = label

                        # Speak only new predictions
                        if label != last_label and confidence > 0.8:
                            tts_engine.say(label)
                            tts_engine.runAndWait()
                            last_label = label
                    else:
                        prediction_placeholder.markdown("✋ Waiting for clear hand gesture...")
                else:
                    prediction_placeholder.markdown("⚠️ No hand detected. Try again...")

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(frame_rgb, channels="RGB", width="stretch")

            cap.release()

# =======================
# 📤 Upload Image Mode
# =======================
elif mode == "📤 Upload Image":
    uploaded_file = st.file_uploader("Upload an image of your ISL sign", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Read and preprocess image
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image_cv = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if image_cv is None:
            st.error("⚠️ Could not read uploaded image. Please try another.")
        else:
            image_cv = cv2.resize(image_cv, (640, 640))
            image_cv = cv2.convertScaleAbs(image_cv, alpha=1.3, beta=25)

            st.image(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB),
                     caption="Uploaded Image",
                     use_container_width=True)

            # Extract landmarks
            landmarks, hand_landmarks = model_handler.extract_landmarks(image_cv)

            if landmarks is not None:
                label, confidence = model_handler.predict_sign(landmarks)
                image_cv = model_handler.draw_landmarks(image_cv, hand_landmarks)

                st.image(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB),
                         caption="Processed with Hand Landmarks",
                         use_container_width=True)

                if label:
                    if sentence_mode:
                        st.session_state.spoken_text += label
                    else:
                        st.session_state.spoken_text = label

                    tts_engine.say(label)
                    tts_engine.runAndWait()

                    st.success(f"✅ Predicted Sign: **{label}** ({confidence * 100:.1f}% confidence)")
                else:
                    st.warning("⚠️ No recognizable sign found.")
            else:
                st.warning("⚠️ No hand detected. Try a clearer image or better lighting.")

# =======================
# 🔊 Output + Controls
# =======================
if st.session_state.spoken_text:
    st.markdown("---")
    st.markdown(f"### 🗣️ Spoken Output: **{st.session_state.spoken_text}**")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔊 Replay Speech"):
            tts_engine.say(st.session_state.spoken_text)
            tts_engine.runAndWait()
    with col2:
        if st.button("🧹 Clear Output"):
            st.session_state.spoken_text = ""
            st.rerun()
    with col3:
        st.info("Use 'Sentence Mode' to form full words or sentences.")

# =======================
# ℹ️ Info Section
# =======================
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("### 💬 How it works")
st.markdown("""
1. Detects hand landmarks using **MediaPipe Hands**  
2. Predicts gesture using your trained **CNN model (final_model.h5)**  
3. Converts prediction into **spoken output** via `pyttsx3`  
4. Supports both **live webcam** and **image upload**  
5. Optional **Sentence Mode** lets you build words interactively
""")
