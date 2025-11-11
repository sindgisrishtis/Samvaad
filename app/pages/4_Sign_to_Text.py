import streamlit as st
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

# Setup paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.model_handler import get_model_handler
from utils.auth import check_login
from utils.theme import apply_theme, get_theme_css

# Streamlit page settings
st.set_page_config(page_title="Sign → Text - Samvaad", page_icon="✋", layout="wide")

# Apply custom theme
apply_theme()
st.markdown(get_theme_css(), unsafe_allow_html=True)

# Redirect to login if user not logged in
if not check_login():
    st.warning("⚠️ Please login to use the translator.")
    st.switch_page("pages/1_login.py")

# Load model handler
model_handler = get_model_handler()

st.markdown("""
    <div class="hero-section">
        <h1 class="main-title">✋ Sign → Text Translator</h1>
        <p class="tagline">Show your ISL sign to the camera and let AI do the talking!</p>
    </div>
""", unsafe_allow_html=True)

# Choose input method
mode = st.radio("Choose input method:", ["📷 Live Camera", "📤 Upload Image"])
st.markdown("---")

# =======================
# 📷 Live Camera Mode
# =======================
if mode == "📷 Live Camera":
    st.info("🎥 Allow camera access and show your hand gesture clearly in front of the webcam.")

    run = st.checkbox("Start Webcam")

    if run:
        frame_placeholder = st.empty()
        prediction_placeholder = st.empty()

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("🚫 Unable to access camera. Please check permissions.")
        else:
            while run:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to read from webcam.")
                    break

                frame = cv2.flip(frame, 1)

                # ✅ Added: Resize and enhance contrast for better hand detection
                frame = cv2.resize(frame, (640, 480))
                frame = cv2.convertScaleAbs(frame, alpha=1.3, beta=25)

                # Extract landmarks
                landmarks, hand_landmarks = model_handler.extract_landmarks(frame)

                if landmarks is not None:
                    label, confidence = model_handler.predict_sign(landmarks)
                    frame = model_handler.draw_landmarks(frame, hand_landmarks)
                    prediction_placeholder.markdown(
                        f"### 🧠 Prediction: **{label}** ({confidence:.1%} confidence)"
                    )
                else:
                    prediction_placeholder.markdown("✋ Waiting for clear hand gesture...")

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(frame_rgb, channels="RGB", width="stretch")

            cap.release()

# =======================
# 📤 Upload Image Mode
# =======================
elif mode == "📤 Upload Image":
    uploaded_file = st.file_uploader("Upload an image of your ISL sign", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # ✅ Read image correctly as OpenCV array
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image_cv = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if image_cv is None:
            st.error("⚠️ Could not read uploaded image. Please try another.")
        else:
            # ✅ Resize + Brighten (critical fix)
            image_cv = cv2.resize(image_cv, (640, 640))
            image_cv = cv2.convertScaleAbs(image_cv, alpha=1.3, beta=25)

            st.image(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB), caption="Uploaded Image", use_container_width=True)

            # ✅ Extract landmarks (on brightened image)
            landmarks, hand_landmarks = model_handler.extract_landmarks(image_cv)

            if landmarks is not None:
                label, confidence = model_handler.predict_sign(landmarks)
                image_cv = model_handler.draw_landmarks(image_cv, hand_landmarks)

                st.image(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB),
                         caption="Processed with Hand Landmarks",
                         use_container_width=True)
                st.success(f"✅ Predicted Sign: **{label}** ({confidence * 100:.1f}% confidence)")
            else:
                st.warning("⚠️ No hands detected. Try a clearer image or better lighting.")

# =======================
# ℹ️ Info Section
# =======================
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("### 💬 How it works")
st.markdown("""
1. Captures hand landmarks using **MediaPipe Hands**  
2. Extracts coordinates and feeds them into the trained CNN model  
3. Model predicts the sign (A-Z or 0-9)  
4. Displays text output in real-time or from image upload
""")
