import os
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
import joblib

# ====== Paths ======
BASE_DIR = "/Users/srishtisindgi/samvaad_project"
MODEL_PATH = os.path.join(BASE_DIR, "outputs", "final_model.h5")
ENCODER_PATH = os.path.join(BASE_DIR, "outputs", "label_encoder.pkl")
TEST_DIR = os.path.join(BASE_DIR, "test_samples")

# ====== Load Model and Encoder ======
model = tf.keras.models.load_model(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)

print("✅ Model and label encoder loaded successfully!\n")

# ====== Initialize MediaPipe ======
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def extract_landmarks(image):
    with mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5) as hands:
        results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if results.multi_hand_landmarks:
            landmarks = results.multi_hand_landmarks[0]
            data = []
            for lm in landmarks.landmark:
                data.extend([lm.x, lm.y, lm.z])
            return np.array(data)
        else:
            return None

# ====== Prediction Helper ======
def predict_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return None, "❌ Cannot read file"
    
    landmarks = extract_landmarks(image)
    if landmarks is None:
        return None, "⚠️ No hand detected"
    
    features = np.expand_dims(landmarks, axis=0)
    predictions = model.predict(features)
    predicted_class = np.argmax(predictions, axis=1)[0]
    predicted_label = label_encoder.inverse_transform([predicted_class])[0]
    return predicted_label, None

# ====== Loop Through All Test Images ======
for label_folder in sorted(os.listdir(TEST_DIR)):
    folder_path = os.path.join(TEST_DIR, label_folder)
    if not os.path.isdir(folder_path):
        continue

    print(f"\n🔤 Testing samples for label: {label_folder}")
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        predicted_label, error = predict_image(file_path)

        if error:
            print(f"  {file_name}: {error}")
        else:
            status = "✅ CORRECT" if predicted_label == label_folder else f"❌ WRONG (Predicted: {predicted_label})"
            print(f"  {file_name}: {status}")
