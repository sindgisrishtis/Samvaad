# pages/9_Practice.py
import streamlit as st
import random
import time
import numpy as np
import cv2
from pathlib import Path
import sqlite3
from datetime import datetime
from PIL import Image
import pandas as pd

# Project imports
from utils.auth import check_login, get_user_info
from utils.model_handler import get_model_handler
from utils.theme import apply_theme, get_theme_css

# -------------------- Page Setup --------------------
st.set_page_config(page_title="🎯 Practice Mode - Samvaad", page_icon="🎯", layout="wide")
apply_theme()
st.markdown(get_theme_css(), unsafe_allow_html=True)

if not check_login():
    st.warning("⚠️ Please login to use Practice Mode.")
    st.switch_page("pages/1_🔐_Login.py")

user_info = get_user_info()
model_handler = get_model_handler()

# -------------------- Database --------------------
DB_PATH = Path(__file__).resolve().parents[1] / "app_data" / "practice_stats.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS practice_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            mode TEXT,
            target TEXT,
            result TEXT,
            score REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def log_practice(user_id, mode, target, result, score):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO practice_history (user_id, mode, target, result, score, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, mode, target, result, score,
          datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# -------------------- Helpers --------------------
def render_frame_with_landmarks(frame, hand_landmarks):
    img = frame.copy()
    img = model_handler.draw_landmarks(img, hand_landmarks)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def majority_vote(preds_list):
    if not preds_list:
        return None, 0
    vals, counts = np.unique(preds_list, return_counts=True)
    idx = np.argmax(counts)
    return vals[idx], int(counts[idx])

# -------------------- UI Header --------------------
st.markdown("""
<div class="hero-section">
    <h1 class="main-title">🎯 Practice Mode</h1>
    <p class="tagline">Interactive practice with stable detection logic</p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# -------------------- Target Persistence --------------------
if "practice_target" not in st.session_state:
    st.session_state.practice_target = random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))

target_letter = st.session_state.practice_target

# -------------------- Mode Selection --------------------
col1, col2 = st.columns([3, 1])
with col1:
    mode = st.radio(
        "Choose practice type:",
        ["🖐️ Text → Sign (identify)", "📷 Sign → Text (show sign)"],
        horizontal=True
    )

with col2:
    if st.button("🔁 New Target"):
        st.session_state.practice_target = random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
        st.session_state.pop("live_preds", None)
        st.session_state.pop("confirmed", None)

st.markdown("---")

# ==========================================================
# 🖐️ TEXT → SIGN  (NO TARGET SHOWN)
# ==========================================================
if mode.startswith("🖐️"):
    st.subheader("🧠 Identify the Correct Sign")

    templates_path = Path(__file__).resolve().parents[2] / "outputs" / "text_to_sign" / "images"

    img_file = None
    for suf in (".jpg", ".png", ".jpeg"):
        fp = templates_path / f"{target_letter}{suf}"
        if fp.exists():
            img_file = fp
            break

    if img_file is None:
        st.warning("⚠️ No sign templates found.")
    else:
        st.image(
            str(img_file),
            caption="What letter does this sign represent?",
            width=220
        )

        guess = st.text_input("Enter your guess (A–Z):").strip().upper()

        if guess:
            if guess == target_letter:
                st.success("✅ Correct!")
                score = 1.0
            else:
                st.error("❌ Incorrect")
                score = 0.0

            st.info(f"🎯 Correct answer: **{target_letter}**")
            log_practice(user_info["user_id"], "Text→Sign", target_letter, guess, score)

        if st.button("🔁 Try Another"):
            st.session_state.practice_target = random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
            st.session_state.pop("live_preds", None)
            st.rerun()

# ==========================================================
# 🤟 SIGN → TEXT  (TARGET SHOWN)
# ==========================================================
else:
    st.subheader("🤟 Show the Correct Sign (hold steady)")
    st.markdown(f"### 🎯 Target Letter: **{target_letter}**")

    cols = st.columns(3)
    with cols[0]:
        frames_required = st.slider("Frames to aggregate", 3, 12, 6)
    with cols[1]:
        min_votes = st.slider("Votes required", 2, frames_required, int(frames_required * 0.6))
    with cols[2]:
        conf_threshold = st.slider("Confidence threshold", 0.4, 0.95, 0.6, 0.05)

    input_method = st.radio("Input Method:", ["📷 Live Camera", "📤 Upload Image"], horizontal=True)
    st.markdown("---")

    if "live_preds" not in st.session_state:
        st.session_state.live_preds = []
        st.session_state.live_confs = []
        st.session_state.confirmed = False

    # ---------------- Live Camera ----------------
    if input_method == "📷 Live Camera":
        run = st.checkbox("🎥 Start Webcam")
        placeholder = st.empty()
        status = st.empty()
        progress = st.progress(0)

        if run:
            cap = cv2.VideoCapture(0)
            st.session_state.live_preds.clear()
            st.session_state.live_confs.clear()

            while len(st.session_state.live_preds) < frames_required:
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)
                frame = cv2.resize(frame, (640, 480))
                landmarks, hand_landmarks = model_handler.extract_landmarks(frame)

                if landmarks is not None:
                    label, conf = model_handler.predict_sign(landmarks)
                    st.session_state.live_preds.append(label)
                    st.session_state.live_confs.append(conf or 0.0)
                    shown = render_frame_with_landmarks(frame, hand_landmarks)
                else:
                    st.session_state.live_preds.append("None")
                    st.session_state.live_confs.append(0.0)
                    shown = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                placeholder.image(shown, use_column_width=True)
                progress.progress(int(len(st.session_state.live_preds) / frames_required * 100))
                time.sleep(0.12)

            cap.release()

            maj, votes = majority_vote(st.session_state.live_preds)
            avg_conf = np.mean(st.session_state.live_confs)

            status.markdown(f"**Detected:** {maj} | votes={votes} | conf={avg_conf:.2f}")

            if maj and votes >= min_votes and avg_conf >= conf_threshold:
                st.success("Detection accepted")
                if st.button("✅ Log Result"):
                    score = 1.0 if maj == target_letter else 0.0
                    log_practice(user_info["user_id"], "Sign→Text", target_letter, maj, score)
                    st.success("Logged!")
            else:
                st.warning("Detection unstable")

    # ---------------- Upload Image ----------------
    else:
        uploaded = st.file_uploader("Upload image", ["jpg", "jpeg", "png"])
        if uploaded:
            file_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            img = cv2.resize(img, (640, 640))

            landmarks, hand_landmarks = model_handler.extract_landmarks(img)
            label, conf = model_handler.predict_sign(landmarks) if landmarks is not None else (None, 0.0)

            shown = render_frame_with_landmarks(img, hand_landmarks) if hand_landmarks else cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            st.image(shown, caption=f"Predicted: {label} ({conf:.2f})")

            if st.button("✅ Log Result"):
                score = 1.0 if label == target_letter else 0.0
                log_practice(user_info["user_id"], "Sign→Text", target_letter, label, score)
                st.success("Logged!")

# -------------------- Summary --------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("### 📊 Your Practice Summary")

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query(
    "SELECT timestamp, mode, target, result, score FROM practice_history WHERE user_id=? ORDER BY id DESC LIMIT 20",
    conn,
    params=(user_info["user_id"],)
)
conn.close()

if not df.empty:
    df["Result"] = df["score"].apply(lambda x: "✅" if x == 1 else "❌")
    st.dataframe(df[["timestamp", "mode", "target", "result", "Result"]], use_container_width=True)
else:
    st.info("No practice records yet.")
