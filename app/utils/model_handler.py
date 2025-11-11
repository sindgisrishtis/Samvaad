import cv2
import numpy as np
import mediapipe as mp
from pathlib import Path
import pickle

class ModelHandler:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,         # Continuous tracking (for webcam + image)
            max_num_hands=2,                 # ✅ Detect both hands
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

        # ✅ Define base project path
        self.base_path = Path(__file__).resolve().parents[2]

        # ✅ Model and Encoder paths
        self.model_path = self.base_path / "outputs" / "final_model.h5"
        self.label_encoder_path = self.base_path / "outputs" / "label_encoder.pkl"

        # ✅ Templates folder (used for text → sign)
        self.templates_path = self.base_path / "outputs" / "text_to_sign" / "images"

        # Load model and encoder
        self.model = None
        self.label_encoder = None
        self.load_model()

    def load_model(self):
        """Load trained model and label encoder"""
        try:
            import tensorflow as tf

            if self.model_path.exists():
                self.model = tf.keras.models.load_model(str(self.model_path))
                print(f"✅ Model loaded from: {self.model_path}")
            else:
                print(f"⚠️ Model not found at: {self.model_path}")

            if self.label_encoder_path.exists():
                with open(self.label_encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                print(f"✅ Label encoder loaded from: {self.label_encoder_path}")
            else:
                print(f"⚠️ Label encoder not found at: {self.label_encoder_path}")

            return True

        except Exception as e:
            print(f"❌ Error loading model or encoder: {e}")
            return False

    def extract_landmarks(self, image):
        """Extract hand landmarks from image"""
        try:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.hands.process(image_rgb)

            if not results.multi_hand_landmarks:
                return None, None

            # ✅ Use first detected hand for consistency
            hand_landmarks = results.multi_hand_landmarks[0]
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])

            # ✅ Ensure exactly 63 features (21 landmarks * 3)
            landmarks = landmarks[:63]
            while len(landmarks) < 63:
                landmarks.extend([0, 0, 0])

            return np.array(landmarks), [hand_landmarks]

        except Exception as e:
            print(f"❌ Error extracting landmarks: {e}")
            return None, None

    def predict_sign(self, landmarks):
        """Predict sign from landmarks"""
        if self.model is None or self.label_encoder is None:
            print("⚠️ Model or label encoder not loaded.")
            return None, 0.0

        try:
            landmarks = np.array(landmarks).reshape(1, -1)
            prediction = self.model.predict(landmarks, verbose=0)

            predicted_class = np.argmax(prediction)
            confidence = float(np.max(prediction))
            label = self.label_encoder.inverse_transform([predicted_class])[0]

            return label, confidence

        except Exception as e:
            print(f"❌ Error predicting: {e}")
            return None, 0.0

    def draw_landmarks(self, image, hand_landmarks):
        """Draw hand landmarks on image"""
        if hand_landmarks:
            for landmarks in hand_landmarks:
                self.mp_draw.draw_landmarks(
                    image,
                    landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_draw.DrawingSpec(color=(255, 255, 255), thickness=1)
                )
        return image

    def calculate_similarity(self, landmarks1, landmarks2):
        """Calculate cosine similarity between two landmark sets"""
        try:
            if landmarks1 is None or landmarks2 is None:
                return 0.0

            l1 = np.array(landmarks1) / np.linalg.norm(landmarks1)
            l2 = np.array(landmarks2) / np.linalg.norm(landmarks2)
            similarity = np.dot(l1, l2)

            return max(0.0, min(1.0, float(similarity)))
        except Exception as e:
            print(f"❌ Error calculating similarity: {e}")
            return 0.0

    def get_sign_template(self, letter):
        """Get stored template for a letter"""
        template_file = self.templates_path / f"{letter.upper()}.npy"
        if template_file.exists():
            return np.load(template_file)
        return None

    def save_sign_template(self, letter, landmarks):
        """Save landmarks as template for a letter"""
        self.templates_path.mkdir(parents=True, exist_ok=True)
        template_file = self.templates_path / f"{letter.upper()}.npy"
        np.save(template_file, landmarks)


# ✅ Singleton instance
_model_handler = None

def get_model_handler():
    global _model_handler
    if _model_handler is None:
        _model_handler = ModelHandler()
    return _model_handler
