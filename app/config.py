import firebase_admin
from firebase_admin import credentials, firestore
import torch
import whisper
import warnings
import google.generativeai as genai

# ------------------------------
# Firebase Initialization
# ------------------------------
FIREBASE_CERT = "/mnt/02269F95269F8875/DEV/vitalgenie/app/vitalgenie-firebase-adminsdk-fbsvc-cd12c49878.json"  # Replace with your file path
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CERT)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ------------------------------
# Google Gemini Configuration
# ------------------------------
GOOGLE_API_KEY = ""  # Replace with your API key
genai.configure(api_key=GOOGLE_API_KEY)
# Initialize the Gemini model (adjust the model name as needed)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# ------------------------------
# GPU Setup and Whisper Model Loading
# ------------------------------
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🚀 Running on: {DEVICE}")
if DEVICE.type == "cuda":
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True

MODEL_NAME = "tiny"  # You can change this to a larger model if needed
print(f"🔹 Loading Whisper Model: {MODEL_NAME}...")
whisper_model = whisper.load_model(MODEL_NAME).to(DEVICE)

# Optionally, filter warnings from torchaudio
warnings.filterwarnings("ignore", category=UserWarning, module="torchaudio")
