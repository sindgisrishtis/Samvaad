import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import pickle

# -----------------------------
# Load model and label encoder
# -----------------------------
model = tf.keras.models.load_model("../outputs/final_model.h5")
with open("../outputs/label_encoder.pkl", "rb") as f:
    le = pickle.load(f)

# -----------------------------
# Initialize MediaPipe Hands
# -----------------------------
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# -----------------------------
# Webcam Setup
# -----------------------------
cap = cv2.VideoCapture(0)
print("✅ Webcam started — show your ISL gesture in front of the camera!")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip frame for natural interaction
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Convert to RGB for MediaPipe
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Extract landmark coordinates
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])

            # Convert to numpy and reshape
            X_input = np.array(landmarks).reshape(1, -1)

            # Predict gesture
            prediction = model.predict(X_input, verbose=0)
            pred_class = np.argmax(prediction)
            label = le.inverse_transform([pred_class])[0]

            # Draw landmarks and prediction label
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            cv2.putText(frame, f"{label}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 
                        2, (0, 255, 0), 3, cv2.LINE_AA)

    cv2.imshow("Samvaad - Live Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
