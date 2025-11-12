# pages/9_Practice.py  (replace your practice page)
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

# Project imports (assumes same utils as your project)
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

# DB (same as before)
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
    """, (user_id, mode, target, result, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# -------------------- Helpers --------------------
def render_frame_with_landmarks(frame, hand_landmarks):
    """Return RGB image with landmarks drawn (using model_handler.draw_landmarks)."""
    img = frame.copy()
    img = model_handler.draw_landmarks(img, hand_landmarks)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def majority_vote(preds_list):
    """Count the most frequent prediction and return (label, count)."""
    if not preds_list:
        return None, 0
    vals, counts = np.unique(preds_list, return_counts=True)
    idx = np.argmax(counts)
    return vals[idx], int(counts[idx])

# -------------------- UI --------------------
st.markdown("""
<div class="hero-section">
    <h1 class="main-title">🎯 Practice Mode</h1>
    <p class="tagline">Interactive practice with stable detection logic (majority vote + confidence threshold)</p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# persist target letter until user requests new one
if "practice_target" not in st.session_state:
    st.session_state.practice_target = random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    st.session_state.last_try_time = None

col_top1, col_top2 = st.columns([3, 1])
with col_top1:
    st.write("Choose practice type:")
    mode = st.radio("", ["🖐️ Text → Sign (identify)", "📷 Sign → Text (show sign)"], horizontal=True)
with col_top2:
    if st.button("🔁 New Target"):
        st.session_state.practice_target = random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
        st.session_state.pop("live_preds", None)
        st.session_state.pop("confirmed", None)

target_letter = st.session_state.practice_target
st.markdown(f"### 🖐 Practice target: **{target_letter}**")

st.markdown("---")

# ---- Text -> Sign (identify image shown) ----
if mode.startswith("🖐️"):
    st.subheader("🧠 Identify the Correct Sign")
    templates_path = Path(__file__).resolve().parents[2] / "outputs" / "text_to_sign" / "images"
    # find an image for the target
    img_file = None
    for suf in (".jpg", ".png", ".jpeg"):
        fp = templates_path / f"{target_letter}{suf}"
        if fp.exists():
            img_file = fp
            break

    if img_file is None:
        st.warning("⚠️ No sign templates found. Please generate sign images first.")
    else:
        st.image(str(img_file), caption=f"What letter does this sign represent? (Target is {target_letter})", width=220)
        guess = st.text_input("Enter your guess (A–Z):").strip().upper()
        if guess:
            if guess == target_letter:
                st.success("✅ Correct!")
                score = 1.0
            else:
                st.error(f"❌ Incorrect — correct is {target_letter}")
                score = 0.0
            log_practice(user_info['user_id'], "Text→Sign", target_letter, guess, score)

        if st.button("🔁 Try Another"):
            st.session_state.practice_target = random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
            st.session_state.pop("live_preds", None)
            st.rerun()


# ---- Sign -> Text (user shows sign via webcam / upload) ----
else:
    st.subheader("🤟 Show the Correct Sign (hold steady until detection finalizes)")

    # parameters for stability & confidence
    st.markdown("**Detection settings (adjust if needed):**")
    cols = st.columns(3)
    with cols[0]:
        frames_required = st.slider("Frames to aggregate", min_value=3, max_value=12, value=6, help="Number of consecutive frames used for majority vote")
    with cols[1]:
        min_votes = st.slider("Votes required", min_value=2, max_value=frames_required, value=int(frames_required*0.6), help="Minimum votes required for majority")
    with cols[2]:
        conf_threshold = st.slider("Confidence threshold", min_value=0.4, max_value=0.95, value=0.60, step=0.05)

    input_method = st.radio("Input Method:", ["📷 Live Camera", "📤 Upload Image"], horizontal=True)
    st.markdown("---")

    # prepare live prediction buffer in session_state
    if "live_preds" not in st.session_state:
        st.session_state.live_preds = []
        st.session_state.live_confs = []
        st.session_state.captured_image = None
        st.session_state.confirmed = False

    # ----- Live Camera -----
    if input_method == "📷 Live Camera":
        run = st.checkbox("🎥 Start Webcam")
        placeholder = st.empty()
        status = st.empty()
        progress = st.progress(0)

        if run:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                st.error("🚫 Cannot open webcam")
            else:
                start = time.time()
                st.session_state.live_preds = []
                st.session_state.live_confs = []
                st.session_state.captured_image = None
                st.session_state.confirmed = False

                # read until we collect enough frames or user stops
                while len(st.session_state.live_preds) < frames_required:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame = cv2.flip(frame, 1)
                    # small preproc to help detection (resize)
                    small = cv2.resize(frame, (640, 480))
                    landmarks, hand_landmarks = model_handler.extract_landmarks(small)

                    if landmarks is not None:
                        label, confidence = model_handler.predict_sign(landmarks)
                        # store predicted label and confidence
                        st.session_state.live_preds.append(label if label is not None else "None")
                        st.session_state.live_confs.append(confidence if confidence is not None else 0.0)
                        # show frame with landmarks
                        img_shown = render_frame_with_landmarks(small, hand_landmarks)
                    else:
                        st.session_state.live_preds.append("None")
                        st.session_state.live_confs.append(0.0)
                        img_shown = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

                    # update UI
                    placeholder.image(img_shown, use_column_width=True)
                    progress.progress(int(len(st.session_state.live_preds) / frames_required * 100))
                    status.markdown(f"Collected frames: **{len(st.session_state.live_preds)} / {frames_required}**")
                    # small sleep so webcam updates properly
                    time.sleep(0.12)

                cap.release()

                # aggregate results
                majority_label, votes = majority_vote(st.session_state.live_preds)
                avg_conf = float(np.mean(st.session_state.live_confs)) if st.session_state.live_confs else 0.0

                # show summary and captured image
                status.markdown(f"**Majority:** {majority_label} ({votes} votes) — avg confidence {avg_conf:.2f}")
                if st.session_state.captured_image is None:
                    # store last displayed frame (convert to PIL) for user to confirm
                    try:
                        st.session_state.captured_image = Image.fromarray(img_shown)
                    except Exception:
                        st.session_state.captured_image = None

                if majority_label is not None and majority_label != "None" and votes >= min_votes and avg_conf >= conf_threshold:
                    st.success(f"Detected: {majority_label} (accepted)")
                    # auto-confirm (but give user option to override)
                    st.session_state.detected_label = majority_label
                    st.session_state.detected_conf = avg_conf
                    if st.button("✅ Accept detection and log"):
                        score = 1.0 if majority_label == target_letter else 0.0
                        log_practice(user_info['user_id'], "Sign→Text", target_letter, majority_label, score)
                        st.session_state.confirmed = True
                else:
                    st.warning("Detection inconsistent or confidence too low. Try holding the sign steady, increase lighting, or adjust settings.")
                    st.info("You can still inspect the captured frame and press 'Force Accept' if you want.")
                    if st.button("⚠️ Force Accept and Log"):
                        # log current majority even if below threshold
                        majority_label = majority_label if majority_label is not None else "None"
                        score = 1.0 if majority_label == target_letter else 0.0
                        log_practice(user_info['user_id'], "Sign→Text", target_letter, majority_label, score)
                        st.session_state.confirmed = True

                # show captured image & details
                if st.session_state.captured_image:
                    st.image(st.session_state.captured_image, caption=f"Captured (avg conf {avg_conf:.2f})", width=300)

                if st.session_state.confirmed:
                    st.success("Result logged. Click 'Try Another' to practice another letter.")
                    if st.button("🔁 Try Another"):
                        st.session_state.practice_target = random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
                        st.session_state.pop("live_preds", None)
                        st.rerun()

        else:
            st.info("Start the webcam above to practice. Hold the sign steady for the collection period.")

    # ----- Upload Image -----
    else:
        uploaded_file = st.file_uploader("Upload your sign image (single frame):", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            # decode image
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image_cv = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            if image_cv is None:
                st.error("Could not read image.")
            else:
                image_cv = cv2.resize(image_cv, (640, 640))
                # try prediction on original and flipped image, average probabilities
                landmarks, hand_landmarks = model_handler.extract_landmarks(image_cv)
                pred_label = None
                pred_conf = 0.0

                if landmarks is not None:
                    label, conf = model_handler.predict_sign(landmarks)
                    pred_label = label
                    pred_conf = conf if conf is not None else 0.0

                # also try flipped horizontally (helps if handedness differs)
                flipped = cv2.flip(image_cv, 1)
                landmarks_f, hand_landmarks_f = model_handler.extract_landmarks(flipped)
                if landmarks_f is not None:
                    label_f, conf_f = model_handler.predict_sign(landmarks_f)
                    # choose label with higher confidence between two
                    if conf_f is not None and conf_f > pred_conf:
                        pred_label = label_f
                        pred_conf = conf_f

                # render image with landmarks if available
                if hand_landmarks:
                    shown = render_frame_with_landmarks(image_cv, hand_landmarks)
                elif hand_landmarks_f:
                    shown = render_frame_with_landmarks(flipped, hand_landmarks_f)
                else:
                    shown = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)

                st.image(shown, caption=f"Predicted: {pred_label} (conf {pred_conf:.2f})", width=360)

                # accept logic
                if pred_label is not None and pred_label != "None" and pred_conf >= conf_threshold:
                    st.success(f"Detected: {pred_label} (accepted)")
                    if st.button("✅ Accept and Log"):
                        score = 1.0 if pred_label == target_letter else 0.0
                        log_practice(user_info['user_id'], "Sign→Text", target_letter, pred_label, score)
                        st.success("Logged. Click 'Try Another' to continue.")
                        if st.button("🔁 Try Another"):
                            st.session_state.practice_target = random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
                            st.experimental_rerun()
                else:
                    st.warning("Low confidence or no valid sign detected. Try another photo or hold sign closer to the camera.")
                    if st.button("⚠️ Force Accept and Log"):
                        pred = pred_label if pred_label is not None else "None"
                        score = 1.0 if pred == target_letter else 0.0
                        log_practice(user_info['user_id'], "Sign→Text", target_letter, pred, score)
                        st.success("Logged (forced). Click 'Try Another' to continue.")
                        if st.button("🔁 Try Another"):
                            st.session_state.practice_target = random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
                            st.rerun()

# -------------------- Practice Summary --------------------
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("### 📊 Your Practice Summary")

try:
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT mode, target, result, score, timestamp FROM practice_history WHERE user_id=? ORDER BY id DESC LIMIT 20"
    df = None
    df = pd.read_sql_query(query, conn, params=(user_info['user_id'],))
    conn.close()

    if df is not None and not df.empty:
        df['Result'] = df['score'].apply(lambda s: "✅" if s == 1 else "❌")
        # show a friendly table
        st.dataframe(df[['timestamp', 'mode', 'target', 'result', 'Result']], use_container_width=True)
    else:
        st.info("No practice records yet. Start a session above!")
except Exception as e:
    st.error(f"Error fetching history: {e}")
