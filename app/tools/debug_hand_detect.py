import cv2
import numpy as np
import mediapipe as mp
from pathlib import Path

# Automatically pick the first image from your 'A' dataset folder
data_dir = Path("/Users/srishtisindgi/samvaad_project/data/A")
all_images = list(data_dir.glob("*.jpg"))

if not all_images:
    print("❌ No images found in:", data_dir)
    exit(1)

# Pick one sample image (first one)
IMG = all_images[0]
print("🖼️ Testing image:", IMG)

OUT = Path("/Users/srishtisindgi/samvaad_project/hand_debug.jpg")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.3,
    min_tracking_confidence=0.3
)
mp_draw = mp.solutions.drawing_utils

img = cv2.imread(str(IMG))
if img is None:
    print("❌ ERROR: Could not read image:", IMG)
    exit(1)

img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
results = hands.process(img_rgb)

if results.multi_hand_landmarks:
    print(f"✅ Detected {len(results.multi_hand_landmarks)} hand(s)")
    for hand_landmarks in results.multi_hand_landmarks:
        mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    cv2.imwrite(str(OUT), img)
    print("💾 Saved debug image at:", OUT)
else:
    print("⚠️ No hands detected. Try another image or adjust confidence.")
