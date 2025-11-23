**🧏‍♂️ Samvaad – Indian Sign Language (ISL) Translator**
A multi-modal AI-powered communication assistant bridging the gap between speech, text, and sign language.

__🚀 About the Project__
Samvaad is an AI-powered application that enables seamless communication with the Indian Deaf community by translating between:
✔ Sign → Text
✔ Sign → Speech
✔ Text → Sign
✔ Speech → Sign
✔ Practice Mode for Learning ISL
✔ Analytics Dashboard
The system uses MediaPipe, Deep Learning, and Computer Vision to detect hand landmarks and classify them into Indian Sign Language alphabets and numbers.

__🎯 Key Features__
⭐ 1. Sign → Text
Uses webcam or uploaded images
Detects hand landmarks using MediaPipe
Classifies static signs (A–Z, 0–9) using a trained deep learning model
Displays recognized text with confidence score
⭐ 2. Sign → Speech
Converts recognized signs into natural audio
Supports sentence mode
Helps non-signers understand signers in real-time
⭐ 3. Text → Sign
Converts typed text into corresponding ISL sign visuals
Displays dynamic landmark-based renderings
Shows template dataset images (reference images)
⭐ 4. Speech → Sign
Converts live speech to text using SpeechRecognition
Translates spoken words into sign images
Supports both mic input and typed text
⭐ 5. Practice Mode
Two learning modes:
Text → Sign: Identify the correct sign from an image
Sign → Text: Show the correct sign via webcam or image upload
Tracks accuracy, attempts, and corrections
Stores performance in practice database
⭐ 6. Analytics Dashboard
Translation insights
Confidence distribution graph
Practice performance over time
Recent activity timeline
Achievements (Gamification)

__🧠 Tech Stack__
🖥️ Frontend & UI
Streamlit
Custom CSS Themes
Plotly
🤖 AI / ML
TensorFlow/Keras
MediaPipe Hands
OpenCV
NumPy
Scikit-learn
🎤 Speech Processing
SpeechRecognition
PyAudio (or mic alternative)
gTTS / pyttsx3 (Text-to-Speech)
🗄️ Database
SQLite
CSV landmark datasets
🔐 Auth
bcrypt for password hashing
SQLite-based user login system
🧰 Dev Tools
Git & GitHub
Python 3.10
Virtual Environments
.gitignore included

__📁 Project Structure__
Samvaad/
│── app/
│   ├── app.py
│   ├── utils/
│   │   ├── auth.py
│   │   ├── model_handler.py
│   │   ├── theme.py
│   ├── tools/
│   │   ├── generate_sign_images.py
│   │   ├── debug_hand_detect.py
│   ├── pages/
│   │   ├── 1_Login.py
│   │   ├── 2_Signup.py
│   │   ├── 3_Dashboard.py
│   │   ├── 4_Sign_to_Text.py
│   │   ├── 5_Sign_to_Speech.py
│   │   ├── 6_Text_to_Sign.py
│   │   ├── 7_Speech_to_Sign.py
│   │   ├── 8_Analytics.py
│   │   ├── 9_Practice.py
│
│── outputs/
│   ├── final_model.h5
│   ├── label_encoder.pkl
│   ├── text_to_sign/templates/
│
│── data/
│── README.md
│── requirements.txt

**⚙️ Installation & Setup__**
1️⃣ Clone the Repository
git clone https://github.com/sindgisrishtis/Samvaad.git
cd Samvaad
2️⃣ Create a Virtual Environment
conda create -n samvaad python=3.10
conda activate samvaad
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Run the App
cd app
streamlit run app.py

__📦 Model__
Trained on custom ISL alphabet dataset
Uses hand landmark (21 points × 3 coordinates) extracted via MediaPipe
Deep learning model (Dense + Dropout layers)
Classifies 36 classes: A–Z + 0–9

__🧪 How it Works__
Pipeline
Frame capture (Image / Webcam)
MediaPipe detects hand landmarks
Landmarks normalized and fed into model
Model predicts ISL letter
Output converted to text/speech/sign accordingly

__🚀 Future Enhancements__
✔ Add continuous gesture recognition (dynamic signs)
✔ Add sentence prediction using LSTM / Transformers
✔ Deploy on cloud (Streamlit Cloud / HuggingFace Spaces / Azure)
✔ Mobile app version (Flutter + TensorFlow Lite)
✔ Add full ISL gestures beyond alphabets

**🤝 Contributing**
Pull requests are welcome!
For major changes, open an issue first to discuss what you’d like to improve.

**💬 Contact**
👤 Srishti S Sindgi
📧 Your email : sindgisrishti@gmail.com
🔗 GitHub: https://github.com/sindgisrishtis

👤 Ujwala Shet
📧 Your email : ujwalashet389@gmail.com
🔗 GitHub: https://github.com/ujwalashet

