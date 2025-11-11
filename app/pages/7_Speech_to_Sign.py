import streamlit as st
import os
import time
import random
import numpy as np
import cv2
import speech_recognition as sr
from pathlib import Path
from PIL import Image
import mediapipe as mp

# ============================
# 🎯 Streamlit Page Setup
# ============================
st.set_page_config(page_title="Speech → Sign - Samvaad", page_icon="🗣️", layout="wide")

st.markdown("""
    <div style="text-align:center;">
        <h1>🗣️ Speech → Sign Translator</h1>
        <p style="font-size:18px;">Speak or type your message and see it translated into Indian Sign Language (ISL)</p>
    </div>
""", unsafe_allow_html=True)

# ============================
# 🧩 Utility Functions
# ============================
mp_hands = mp.solutions.hands

def render_landmarks_image(landmarks, size=400):
    """Render AI landmarks (.npy) into a hand skeleton image"""
    img = np.ones((size, size, 3), dtype=np.uint8) * 255
    points = []

    try:
        arr = np.array(landmarks).flatten()
        for i in range(0, len(arr), 3):
            x = int(arr[i] * size)
            y = int(arr[i + 1] * size)
            points.append((x, y))

        # Draw connections
        for conn in mp_hands.HAND_CONNECTIONS:
            if conn[0] < len(points) and conn[1] < len(points):
                cv2.line(img, points[conn[0]], points[conn[1]], (0, 255, 0), 2)

        # Draw points
        for p in points:
            cv2.circle(img, p, 5, (0, 0, 255), -1)

    except Exception as e:
        print(f"Error rendering landmarks: {e}")

    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def get_random_dataset_image(letter):
    """Fetch a random dataset image for a letter from /data/<letter>/"""
    dataset_root = Path(__file__).resolve().parents[2] / "data"
    folder = dataset_root / letter.upper()

    if not folder.exists():
        return None

    all_images = list(folder.glob("*.jpg")) + list(folder.glob("*.png"))
    if not all_images:
        return None

    return str(random.choice(all_images))

# ============================
# 🎙️ Input Section
# ============================
mode = st.radio("Choose Input Method:", ["🎙️ Speak", "⌨️ Type Text"])
text_input = ""

if mode == "🎙️ Speak":
    st.info("Click below and speak clearly. Make sure your microphone is enabled in macOS settings.")
    if st.button("🎤 Start Recording"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("🎧 Listening...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            try:
                text_input = recognizer.recognize_google(audio)
                st.success(f"✅ Recognized Speech: **{text_input}**")
            except sr.UnknownValueError:
                st.error("❌ Could not understand audio. Please try again.")
            except sr.RequestError:
                st.error("⚠️ Speech recognition service unavailable.")
else:
    text_input = st.text_input("Enter your text:", placeholder="Type something...")

st.markdown("---")

# ============================
# 🤟 ISL Translation Section
# ============================
if text_input:
    text_input = text_input.upper()
    st.subheader("🤟 ISL Translation:")

    base_path = Path(__file__).resolve().parents[2]
    templates_path = base_path / "outputs" / "text_to_sign" / "templates"

    cols = st.columns(5)
    col_idx = 0

    for letter in text_input:
        if letter == " ":
            time.sleep(0.5)
            continue

        with cols[col_idx % 5]:
            st.markdown(f"### {letter}")

            npy_file = templates_path / f"{letter}.npy"
            jpg_file = templates_path / f"{letter}.jpg"

            # 1️⃣ Try pre-saved AI sign image
            if jpg_file.exists():
                st.image(str(jpg_file), caption=f"AI Stored Sign for {letter}", width=150)

            # 2️⃣ Otherwise try .npy landmark render
            elif npy_file.exists():
                try:
                    data = np.load(npy_file, allow_pickle=True)
                    img = render_landmarks_image(data)
                    st.image(img, caption=f"AI Landmark for {letter}", width=150)
                except Exception as e:
                    st.error(f"❌ Could not load sign for {letter}: {e}")
            else:
                st.warning(f"No AI sign found for '{letter}'")

            # 3️⃣ Dataset image (for visual accuracy)
            dataset_image = get_random_dataset_image(letter)
            if dataset_image:
                st.image(dataset_image, caption=f"Dataset Example for {letter}", width=150)
            else:
                st.info(f"No dataset image found for '{letter}'")

        col_idx += 1
        time.sleep(0.4)  # smooth animation timing per letter

    st.success("✅ Translation complete!")

else:
    st.info("🎙️ Speak or type something to translate into signs.")

# ============================
# 💡 Footer
# ============================
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("""
### 💡 How it works:
1. Converts your speech or text into letters  
2. Loads each letter’s ISL template (`.npy` or `.jpg`)  
3. Renders AI hand landmarks  
4. Displays a real dataset reference for comparison
""")
