import streamlit as st
from pathlib import Path
import numpy as np
import cv2
import mediapipe as mp
import random

from utils.auth import check_login
from utils.model_handler import get_model_handler
from utils.theme import apply_theme, get_theme_css

# ===============================
# 🎯 Function: Fetch random dataset image
# ===============================
def get_random_dataset_image(letter):
    """Fetch a random image for the given letter from dataset folders"""
    dataset_root = Path(__file__).resolve().parents[2] / "data"
    folder = dataset_root / letter.upper()

    if not folder.exists():
        return None

    all_images = list(folder.glob("*.jpg")) + list(folder.glob("*.png"))
    if not all_images:
        return None

    return str(random.choice(all_images))

# ===============================
# 🎨 Function: Render AI landmarks
# ===============================
mp_hands = mp.solutions.hands

def render_landmarks_image(landmarks, size=400):
    """Render .npy landmark data as an image"""
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


# ===============================
# ⚙️ Streamlit page setup
# ===============================
st.set_page_config(page_title="Text → Sign - Samvaad", page_icon="🤟", layout="wide")

apply_theme()
st.markdown(get_theme_css(), unsafe_allow_html=True)

# Check login
if not check_login():
    st.warning("⚠️ Please login to use the translator.")
    st.switch_page("pages/1_login.py")

# Load model handler (for internal use)
model_handler = get_model_handler()

# ===============================
# 🧠 Page UI
# ===============================
st.markdown("""
    <div class="hero-section">
        <h1 class="main-title">🤟 Text → Sign Translator</h1>
        <p class="tagline">Type any letter or number to view the ISL sign visualized from stored landmarks and training samples.</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

user_text = st.text_input("Enter text to translate:", "")

# ===============================
# 🔍 Main Translation Logic
# ===============================
if user_text.strip():
    st.subheader("🤟 ISL Translation:")
    base_path = Path(__file__).resolve().parents[2]
    templates_path = base_path / "outputs" / "text_to_sign" / "templates"

    cols = st.columns(5)
    col_idx = 0

    for letter in user_text.upper():
        with cols[col_idx % 5]:
            st.markdown(f"### {letter}")

            npy_file = templates_path / f"{letter}.npy"
            jpg_file = templates_path / f"{letter}.jpg"

            # 1️⃣ Try displaying stored .jpg (if available)
            if jpg_file.exists():
                st.image(str(jpg_file), caption=f"AI Stored Sign for {letter}", width=150)

            # 2️⃣ Otherwise render from .npy landmarks
            elif npy_file.exists():
                try:
                    data = np.load(npy_file, allow_pickle=True)
                    img = render_landmarks_image(data)
                    st.image(img, caption=f"AI Landmark for {letter}", width=150)
                except Exception as e:
                    st.error(f"❌ Could not load sign for {letter}: {e}")
            else:
                st.warning(f"No AI sign found for '{letter}'")

            # 3️⃣ Add real dataset reference image (for accuracy comparison)
            image_path = get_random_dataset_image(letter)
            if image_path:
                st.image(image_path, caption=f"Dataset Example for {letter}", width=150)
            else:
                st.info(f"No dataset image found for '{letter}'")

        col_idx += 1

    st.success("✅ Translation complete!")

else:
    st.info("✏️ Enter a letter or number to see its sign translation.")

st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("""
### 💡 How it works:
1. Loads pre-saved ISL landmark templates (`.npy`)  
2. Visualizes AI-generated hand skeleton for each letter  
3. Fetches real dataset examples dynamically from your training data  
4. Displays both — for better learning & accuracy understanding
""")
