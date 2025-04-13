
# VitalGenie

VitalGenie is an AI-powered medical assistant platform designed to enhance medical communication, learning, and safety monitoring. It integrates advanced AI models with modern web technologies to offer functionalities such as speech transcription with speaker diarization, retrieval-augmented chat, image analysis, prescription extraction, and real-time monitoring via an ESP32-CAM feed.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture & Rationale](#architecture--rationale)
- [File Structure](#file-structure)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [EHR Report Generation and PDF Download](#ehr-report-generation-and-pdf-download)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Overview

![diagram-export-3-23-2025-9_26_43-AM](https://github.com/user-attachments/assets/9f03d605-3931-4a93-96ef-252ecbfe8bfe)

VitalGenie leverages state-of-the-art AI models and modern web frameworks to provide a seamless user experience for medical professionals and patients. The system handles multiple data types—from audio and text to images—and processes them via various endpoints to deliver real-time insights. The backend is built using FastAPI to ensure high performance and quick development cycles, while the frontend uses Tailwind CSS and Alpine.js to create a responsive, dynamic user interface.

---

## Key Features

- **Speech Transcription & Diarization:**  
  - Uses the Whisper model for audio transcription.
  - Implements speaker diarization via Google Gemini, which segments the transcript by speaker and includes timestamps if available.
  - Stores processed transcription summaries in Firebase Firestore for further retrieval.

- **Retrieval-Augmented Chat (RAG Chat):**  
  - Retrieves the most recent transcription summary from Firestore.
  - Uses FAISS to build a vector index from the transcript for context retrieval.
  - Employs Google Gemini to generate context-aware chat responses.

- **Image Analysis:**  
  - Accepts medical images and leverages Google Gemini for detailed analysis based on predefined prompts.
  
- **Prescription Extraction:**  
  - Extracts prescription details from either conversation text or uploaded images.
  - Outputs the prescription information in structured JSON format.

- **Real-Time Monitoring:**  
  - Continuously monitors patient rooms using an ESP32-CAM feed.
  - Uses Google Gemini to analyze the live video feed for anomalies.
  - Generates alerts and logs monitoring events in Firebase Firestore if an emergency is detected.

- **Electronic Health Record (EHR) Report Generation:**  
  - Automatically generates a comprehensive EHR report from the latest transcription summary.
  - Formats the report into a professional, visually appealing PDF using ReportLab.
  - Allows users to download the EHR PDF via the frontend.

- **User-Friendly Web Interface:**  
  - Single-page application with dedicated pages for Home, Chat, Recording, and Monitoring.
  - Built using HTML, Tailwind CSS, Alpine.js, and custom JavaScript to ensure a modern, interactive experience.

---

## Architecture & Rationale
https://github.com/jebinshaju/vitalgenie/blob/main/app/Readme.md
### Backend (FastAPI API)
- **Technology:**  
  FastAPI is used for its high performance, asynchronous capabilities, and automatic documentation. It is well-suited for developing APIs that handle real-time processing tasks.
  
- **Components:**
  - **Speech Transcription & Diarization:**  
    Audio files are processed with the Whisper model (taking advantage of GPU acceleration when available) for transcription. The resulting transcript is passed to Google Gemini for diarization, which segments the audio based on speaker identity.
    
  - **Retrieval-Augmented Chat:**  
    The `/rag_chat` endpoint retrieves a transcription summary from Firebase Firestore, builds a FAISS index for context retrieval, and then uses Google Gemini to generate a response that is both relevant and empathetic.
    
  - **Image Analysis & Prescription Extraction:**  
    These endpoints process uploaded images and text inputs, sending them to Google Gemini to either analyze the medical image or extract structured prescription details.
    
  - **Monitoring:**  
    A background task continuously fetches an image from the ESP32-CAM and processes it with Google Gemini to check for emergencies. Alerts are generated and logged in Firestore when anomalies are detected.
    
  - **EHR Report Generation:**  
    A dedicated endpoint retrieves the latest transcription summary, constructs a detailed prompt for generating an EHR report, and then creates a well-formatted PDF using ReportLab. This PDF is made available for download.

### Frontend (Web Client)
- **Technology:**  
  The frontend is built as a single-page application (SPA) with:
  - **HTML:** Provides the structure.
  - **Tailwind CSS:** Offers utility-first CSS styling and ensures responsiveness.
  - **Alpine.js:** Handles UI reactivity and state management.
  - **JavaScript:** Manages API interactions, chat functions, audio recording, file uploads, live monitoring updates, and now the EHR PDF download.
  
- **User Interaction:**  
  The UI is divided into multiple sections (Home, Chat, Recording, Monitoring) that allow users to interact with the system, send audio/text/image data, and receive real-time feedback from the backend.

### External Integrations
- **Google Gemini:**  
  Used for generative AI tasks such as transcript diarization, chat response generation, image analysis, prescription extraction, and EHR report creation.
  
- **Whisper Model:**  
  Performs the heavy lifting of transcribing audio into text.
  
- **FAISS:**  
  Provides fast and scalable vector indexing for context retrieval during chat interactions.
  
- **Firebase Firestore:**  
  Acts as the persistence layer, storing transcription summaries, prescription details, monitoring events, and potentially logs for EHR generation.
  
- **ESP32-CAM:**  
  Supplies a live video feed that is analyzed for real-time monitoring.

---

## File Structure

Below is a detailed overview of the project’s directory structure and the purpose of each file:

```
vitalgenie/
├── app/                            # Backend application directory
│   ├── __init__.py                 # Marks the directory as a Python package
│   ├── config.py                   # Configures Firebase, Google Gemini, GPU settings, and loads the Whisper model
│   ├── models.py                   # Contains Pydantic models (e.g., ChatQuery for API requests)
│   ├── main.py                     # FastAPI entry point; sets up middleware, routes, and the startup event
│   ├── routers/                    # Contains modularized API endpoints (routers)
│   │   ├── __init__.py             # Marks the directory as a Python package
│   │   ├── transcribe.py           # Endpoint for audio transcription and speaker diarization
│   │   ├── rag_chat.py             # Endpoint for retrieval-augmented chat
│   │   ├── image_analysis.py       # Endpoint for processing medical images
│   │   ├── prescription.py         # Endpoint for extracting prescription details
│   │   ├── monitoring.py           # Endpoint and background task for real-time monitoring
│   │   └── ehr_pdf.py              # Endpoint for generating and downloading the EHR report as a PDF
│   └── utils/                      # Utility modules for helper functions
│       ├── __init__.py             # Marks the directory as a Python package
│       ├── gemini_utils.py         # Provides functions to interact with Google Gemini
│       ├── faiss_utils.py          # Contains functions for building a FAISS index from summaries
│       └── gpu_utils.py            # Provides helper functions to monitor GPU memory usage
├── css/                            # Frontend CSS directory
│   └── style.css                   # Custom CSS (including Tailwind overrides and chat styling)
├── js/                             # Frontend JavaScript directory
│   └── script.js                   # Contains logic for chat, file uploads, audio recording, live monitoring, and EHR PDF download
├── index.html                      # Main HTML file that defines the single-page application layout and navigation
├── README.md                       # Detailed project documentation (this file)
└── requirements.txt                # List of Python dependencies for the backend
```

![diagram-export-3-23-2025-9_21_19-AM](https://github.com/user-attachments/assets/ff86f3c1-e72a-4ab2-ab4f-184a5e5f95da)

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/jebinshaju/vitalgenie.git
cd vitalgenie
```

### 2. Set Up Python Environment

It is recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Credentials

- **Firebase Credentials:**  
  Place your Firebase service account JSON file in the `app/` directory (e.g., `app/vitalgenie-firebase-adminsdk-fbsvc-cd12c49878.json`).

- **Google Gemini API Key:**  
  Update `app/config.py` with your Google API key for Gemini.

- **Security:**  
  Ensure that these sensitive files are added to your `.gitignore` so they are not pushed to public repositories.

### 4. Run the Backend Server

Start the FastAPI server using uvicorn:

```bash
uvicorn app.main:app --reload
```

### 5. Launch the Frontend

Open `index.html` in your preferred browser. Verify that the `backendURL` in `js/script.js` points to your backend (e.g., `"http://127.0.0.1:8000"`).

---

## Usage

### Chat
- Navigate to the Chat page.
- Type a message and click "Send."
- The message is sent to the `/rag_chat` endpoint and a context-aware response is displayed.

### Audio Transcription
- Go to the Recording page.
- Either record audio using the browser's microphone or upload an audio file.
- Click "Stop Recording" when finished, then click "Upload Recording."
- The audio file is sent to the `/transcribe` endpoint, and the transcription (with diarized output) is displayed.

### Image Analysis & Prescription Extraction
- Use the provided file inputs to upload images.
- Image uploads trigger calls to the `/image_analysis` or `/extract_prescription` endpoints.
- Results (analysis or extracted prescription details) are displayed in the chat window.

### Live Monitoring
- The Monitoring page automatically refreshes the live ESP32-CAM feed.
- The system polls the `/monitor_status` endpoint for updates and displays alerts if an anomaly is detected.

---

## EHR Report Generation and PDF Download

VitalGenie now provides an endpoint to generate a comprehensive Electronic Health Record (EHR) report in PDF format from the latest transcription summary. This report is automatically generated by using a prompt to Google Gemini and then formatted using ReportLab to produce a professional PDF.

**Backend Functionality:**
- **Endpoint:** `/generate_ehr_pdf`
- **Process:**
  1. Retrieves the latest transcription summary from Firebase Firestore.
  2. Constructs a prompt instructing Google Gemini to create a detailed EHR report.
  3. Uses ReportLab’s Platypus to format the generated report into a visually appealing PDF.
  4. The PDF is temporarily stored and returned as a downloadable file.

**Frontend Integration:**
- A "Download EHR Report" button has been added to the Chat page.
- When clicked, the frontend makes a GET request to the `/generate_ehr_pdf` endpoint.
- The PDF is downloaded automatically to the user’s device as `ehr_report.pdf`.

---

## Security Considerations

- **Secrets & Credentials:**  
  Never commit sensitive information (e.g., Firebase credentials, API keys) to your repository. Use a `.gitignore` file and environment variables to manage secrets securely.

- **Credential Rotation:**  
  In case of exposure, immediately rotate your API keys and service account credentials.

- **Push Protection:**  
  GitHub's secret scanning may block pushes containing sensitive data. Follow best practices for secrets management and consult [GitHub's documentation](https://docs.github.com/code-security/secret-scanning) for more information.

---

## Troubleshooting

- **Recording Format Issue:**  
  If you receive errors such as:
  ```json
  { "detail": "Invalid format. Upload a WAV or MP3 file." }
  ```
  it means that the file format is not supported by the backend. Either update the allowed MIME types in the `/transcribe` endpoint or convert the audio format from `"audio/webm"` to a supported format before submission.

- **Backend Connectivity:**  
  Ensure that the `backendURL` in `js/script.js` is correct and that your FastAPI server is running.

- **Dependency Issues:**  
  Double-check that all dependencies in `requirements.txt` are installed in your virtual environment.

---

## Contributing

Contributions are welcome! If you’d like to contribute:
1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Write clear commit messages and document your changes.
4. Submit a pull request for review.

Please adhere to the coding standards and ensure all tests pass before submitting your pull request.

