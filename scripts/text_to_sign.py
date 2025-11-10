"""
text_to_sign.py
Simple demo: type text, it speaks it (pyttsx3) and shows each letter/digit
as a 2D MediaPipe-style skeleton using canonical landmarks (from templates).
Fast, no interpolation. Press ESC to exit anytime.
"""

import os
import time
import json
import numpy as np
import cv2
import mediapipe as mp
import pyttsx3

BASE = "/Users/srishtisindgi/samvaad_project"
TEMPLATE_DIR = os.path.join(BASE, "outputs", "text_to_sign", "templates")
MAPPING_FILE = os.path.join(BASE, "outputs", "text_to_sign", "mapping.json")

# animation parameters
FRAME_W, FRAME_H = 640, 480
DISPLAY_TIME = 0.6   # seconds per letter

# mediapipe drawing utils and connections (hand)
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
HAND_CONNECTIONS = mp_hands.HAND_CONNECTIONS  # use same connections for drawing

# load mapping
with open(MAPPING_FILE, "r") as f:
    mapping = json.load(f)
valid_classes = set(mapping["classes"])

# load templates into dict
templates = {}
for fname in os.listdir(TEMPLATE_DIR):
    if fname.endswith(".npy"):
        label = os.path.splitext(fname)[0]
        templates[label] = np.load(os.path.join(TEMPLATE_DIR, fname))  # shape (63,)

print(f"Loaded {len(templates)} templates: {sorted(templates.keys())}")

# initialize TTS (pyttsx3 offline)
tts = pyttsx3.init()
tts.setProperty('rate', 170)  # speaking rate
tts.setProperty('volume', 1.0)

def landmarks_to_pixel_coords(landmark_vec, w, h):
    """
    Convert normalized landmark vector (63,) -> list of (x_px, y_px) pairs
    landmark_vec order: x0,y0,z0,x1,y1,z1,...
    We ignore z for 2D drawing.
    """
    coords = []
    for i in range(0, len(landmark_vec), 3):
        x = landmark_vec[i] * w
        y = landmark_vec[i+1] * h
        coords.append((int(x), int(y)))
    return coords

def draw_hand_skeleton(frame, coords):
    # draw connections
    for (start_idx, end_idx) in HAND_CONNECTIONS:
        if start_idx < len(coords) and end_idx < len(coords):
            cv2.line(frame, coords[start_idx], coords[end_idx], (0,255,0), 2)
    # draw keypoints
    for (x,y) in coords:
        cv2.circle(frame, (x,y), 4, (0,0,255), -1)

def play_text(text):
    """
    For each char in text, if char in templates, show pose for DISPLAY_TIME seconds.
    Also speak the whole text with TTS at start.
    """
    text = text.upper()
    # speak in background (non-blocking)
    tts.say(text)
    tts.runAndWait()  # blocking so audio and animation sync; remove runAndWait for async

    window_name = "Text→Sign (Samvaad) - Press ESC to quit"
    cv2.namedWindow(window_name)
    for ch in text:
        if ch == " ":
            # small pause for space
            blank = np.zeros((FRAME_H, FRAME_W, 3), dtype=np.uint8)
            cv2.putText(blank, "[space]", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200,200,200), 2)
            cv2.imshow(window_name, blank)
            if cv2.waitKey(int(DISPLAY_TIME*1000)) & 0xFF == 27:
                break
            continue

        if ch not in templates:
            blank = np.zeros((FRAME_H, FRAME_W, 3), dtype=np.uint8)
            cv2.putText(blank, f"[{ch} - no template]", (30, FRAME_H//2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 2)
            cv2.imshow(window_name, blank)
            if cv2.waitKey(int(DISPLAY_TIME*1000)) & 0xFF == 27:
                break
            continue

        vec = templates[ch]  # 63
        coords = landmarks_to_pixel_coords(vec, FRAME_W, FRAME_H)
        frame = np.zeros((FRAME_H, FRAME_W, 3), dtype=np.uint8)
        draw_hand_skeleton(frame, coords)
        cv2.putText(frame, f"{ch}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 2)
        cv2.imshow(window_name, frame)
        # wait for display time or ESC
        if cv2.waitKey(int(DISPLAY_TIME*1000)) & 0xFF == 27:
            break

    cv2.destroyWindow(window_name)

def interactive_loop():
    print("Text→Sign interactive. Type text and press Enter. Type 'exit' to quit.")
    while True:
        txt = input("Enter text: ").strip()
        if not txt:
            continue
        if txt.lower() in ("exit", "quit"):
            break
        play_text(txt)

if __name__ == "__main__":
    interactive_loop()
    print("Done.")
