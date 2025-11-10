import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import pickle
import os

# Load model + label encoder
model = tf.keras.models.load_model("../outputs/final_model.h5")
with open("../outputs/label_encoder.pkl", "rb") as f:
    le = pickle.load(f)

# Initialize mediapipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)

# Path to any test image
test_image = "/Users/srishtisindgi/samvaad_project/data/W/5.jpg"  # Change to any alphabet or digit image

image = cv2.imread(test_image)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
results = hands.process(image_rgb)

if not results.multi_hand_landmarks:
    print("❌ No hand detected in the image.")
else:
    for hand_landmarks in results.multi_hand_landmarks:
        landmarks = []
        for lm in hand_landmarks.landmark:
            landmarks.extend([lm.x, lm.y, lm.z])
        X_input = np.array(landmarks).reshape(1, -1)
        prediction = model.predict(X_input, verbose=0)
        pred_class = np.argmax(prediction)
        label = le.inverse_transform([pred_class])[0]
        print(f"✅ Predicted Sign: {label}")
