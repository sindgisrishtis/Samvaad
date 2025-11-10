import cv2
import mediapipe as mp
import os
import csv

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Paths
DATA_DIR = "/Users/srishtisindgi/samvaad_project/data"
CSV_FILE = "/Users/srishtisindgi/samvaad_project/outputs/landmarks.csv"

# Initialize CSV
header = ["label"]
for i in range(21):
    header += [f"x{i}", f"y{i}", f"z{i}"]

with open(CSV_FILE, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)

# Initialize hand model
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5)

# Loop through dataset
for label in os.listdir(DATA_DIR):
    label_path = os.path.join(DATA_DIR, label)
    if not os.path.isdir(label_path):
        continue

    print(f"Processing label: {label}")

    for img_file in os.listdir(label_path):
        img_path = os.path.join(label_path, img_file)
        image = cv2.imread(img_path)
        if image is None:
            continue
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                row = [label]
                for lm in hand_landmarks.landmark:
                    row += [lm.x, lm.y, lm.z]

                with open(CSV_FILE, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(row)
