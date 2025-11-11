# app/tools/generate_sign_images.py
import numpy as np
import cv2
import mediapipe as mp
from pathlib import Path

templates_path = Path("outputs/text_to_sign/templates")
output_path = Path("outputs/text_to_sign/images")
output_path.mkdir(parents=True, exist_ok=True)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

for file in templates_path.glob("*.npy"):
    data = np.load(file)
    img = np.ones((400, 400, 3), dtype=np.uint8) * 255

    # reshape landmark array
    landmarks = data.reshape(-1, 3)
    for x, y, z in landmarks:
        cx, cy = int(x * 400), int(y * 400)
        cv2.circle(img, (cx, cy), 5, (0, 0, 255), -1)

    cv2.imwrite(str(output_path / f"{file.stem}.jpg"), img)

print("✅ Generated all sign images!")
