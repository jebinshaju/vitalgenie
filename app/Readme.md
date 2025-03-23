

# VitalGenie Backend Detailed Documentation

The backend of VitalGenie is designed using FastAPI to deliver a robust, asynchronous API that handles real-time medical data processing. This documentation covers the architecture, individual modules, endpoints, external integrations, and the rationale behind the implementation.

---

## Table of Contents

- [Overview](#overview)
- [Architecture & Design Principles](#architecture--design-principles)
- [Configuration & External Services](#configuration--external-services)
- [Modules and File Details](#modules-and-file-details)
  - [Core Configuration (`config.py`)](#core-configuration-configpy)
  - [Data Models (`models.py`)](#data-models-modelspy)
  - [Application Entry Point (`main.py`)](#application-entry-point-mainpy)
  - [Routers (Endpoints)](#routers-endpoints)
    - [Transcription & Diarization (`transcribe.py`)](#transcription--diarization-transcribepy)
    - [Retrieval-Augmented Chat (`rag_chat.py`)](#retrieval-augmented-chat-rag_chatpy)
    - [Image Analysis (`image_analysis.py`)](#image-analysis-image_analysispy)
    - [Prescription Extraction (`prescription.py`)](#prescription-extraction-prescriptionpy)
    - [Monitoring (`monitoring.py`)](#monitoring-monitoringpy)
    - [EHR PDF Generation (`ehr_pdf.py`)](#ehr-pdf-generation-ehr_pdfpy)
  - [Utility Modules](#utility-modules)
    - [Google Gemini Utilities (`gemini_utils.py`)](#google-gemini-utilities-gemini_utilspy)
    - [FAISS Index Utilities (`faiss_utils.py`)](#faiss-index-utilities-faiss_utilspy)
    - [GPU Utilities (`gpu_utils.py`)](#gpu-utilities-gpu_utilspy)
- [Asynchronous Processing and Error Handling](#asynchronous-processing-and-error-handling)
- [External Integrations](#external-integrations)
- [Development and Deployment Considerations](#development-and-deployment-considerations)
- [Troubleshooting & Logging](#troubleshooting--logging)
- [Conclusion](#conclusion)

---

## Overview

The VitalGenie backend provides a suite of RESTful endpoints that allow users to process audio, text, and image data for medical applications. It leverages advanced AI models such as Whisper (for transcription) and Google Gemini (for generative tasks like diarization, chat, and EHR generation). Data is stored in Firebase Firestore, and additional functionality such as FAISS-based context retrieval is used for enhanced chat capabilities. The backend also implements a continuous monitoring system via an ESP32-CAM feed.

---

## Architecture & Design Principles

- **Modularity:**  
  The project is divided into distinct modules (routers, utilities, configuration) that separate concerns. This simplifies maintenance, testing, and future enhancements.
  
- **Asynchronous Processing:**  
  FastAPI’s async capabilities allow endpoints to handle I/O-bound operations (e.g., external API calls, file processing) without blocking the server. This is crucial for real-time tasks like transcription and monitoring.
  
- **Separation of Concerns:**  
  - **Configuration and Setup:** All external integrations (Firebase, Google Gemini, GPU configuration) are managed in `config.py`.
  - **API Endpoints:** Each major functionality (transcription, chat, image analysis, etc.) is implemented in its own router, making it easier to manage and update.
  - **Utilities:** Helper functions for Gemini calls, FAISS indexing, and GPU monitoring are centralized for reuse.

- **Robust Error Handling:**  
  Every endpoint includes try/except blocks to capture and return meaningful errors, ensuring stability and easier debugging.

---

## Configuration & External Services

### Firebase Firestore  
Used for persisting transcription summaries, prescription data, and monitoring events. Configuration is performed in `config.py` using a service account file.

### Google Gemini  
An external generative AI service used for:
- Speaker diarization (segmenting transcriptions by speaker)
- Chat response generation
- Image analysis
- Prescription extraction
- Generating EHR reports in plain text (and later PDF formatting)

### Whisper Model  
Used to transcribe audio files into text. The model is loaded with GPU acceleration if available.

### FAISS  
A library for efficient similarity search, used to create an index of transcript sentences for context retrieval in chat interactions.

### ESP32-CAM  
Provides a live video feed that is continuously monitored for anomalies.

---

## Modules and File Details

### Core Configuration (`app/config.py`)

- **Purpose:**  
  This file sets up all external integrations and environmental configurations:
  - Initializes Firebase with the service account credentials.
  - Configures the Google Gemini model with the API key.
  - Detects and configures the GPU environment using PyTorch.
  - Loads the Whisper transcription model.
  
- **Key Code Aspects:**  
  - Uses Firebase Admin SDK for Firestore.
  - Uses torch.device to decide between GPU and CPU.
  - Prints log messages to confirm configuration stages.

### Data Models (`app/models.py`)

- **Purpose:**  
  Contains Pydantic models that validate and structure the incoming API data.  
- **Example:**  
  The `ChatQuery` model ensures that the chat endpoint receives a JSON object with a `query` string.
  
- **Importance:**  
  Enforces type-safety and improves documentation through automatic API docs.

### Application Entry Point (`app/main.py`)

- **Purpose:**  
  Sets up the FastAPI application, configures middleware (like CORS), includes all routers, and starts background tasks (e.g., monitoring).
  
- **Key Code Aspects:**  
  - Imports routers from various modules.
  - Registers startup events to launch background tasks.
  - Uses uvicorn as the ASGI server for development and production.

### Routers (Endpoints)

#### Transcription & Diarization (`app/routers/transcribe.py`)

- **Functionality:**  
  Accepts an audio file, uses the Whisper model for transcription, and then sends the transcript to Google Gemini for speaker diarization.
  
- **Flow:**  
  1. Temporarily saves the uploaded file.
  2. Calls Whisper to transcribe audio.
  3. Constructs a prompt for Gemini to perform diarization.
  4. Saves the diarized transcript in Firestore.
  5. Returns both the raw transcription and the diarized version.

#### Retrieval-Augmented Chat (`app/routers/rag_chat.py`)

- **Functionality:**  
  Provides context-aware chat responses by retrieving relevant parts of the latest transcription summary.
  
- **Flow:**  
  1. Queries Firestore for the latest transcription summary.
  2. Uses Sentence Transformers to create embeddings for each sentence.
  3. Builds a FAISS index for fast similarity search.
  4. Retrieves the most relevant sentences based on the user's query.
  5. Constructs a prompt for Gemini to generate a detailed, empathetic response.
  6. Returns the chat response along with the context.

#### Image Analysis (`app/routers/image_analysis.py`)

- **Functionality:**  
  Accepts an image file and a prompt, then leverages Google Gemini to generate an analysis of the medical image.
  
- **Flow:**  
  1. Validates the file type.
  2. Reads and processes the image.
  3. Passes the image and prompt to Gemini.
  4. Returns the generated analysis text.

#### Prescription Extraction (`app/routers/prescription.py`)

- **Functionality:**  
  Extracts prescription details either from text (conversation) or an image file.
  
- **Flow:**  
  1. Validates input (ensuring either text or an image is provided).
  2. Constructs a prompt instructing Gemini to extract prescription details in JSON format.
  3. Attempts to parse the output and returns a structured JSON.
  4. Stores the extracted data in Firestore.

#### Monitoring (`app/routers/monitoring.py`)

- **Functionality:**  
  Continuously monitors a patient room via an ESP32-CAM feed.
  
- **Flow:**  
  1. A background task periodically fetches an image from the camera.
  2. The image is sent to Gemini with a prompt to detect any anomalies.
  3. Updates a global monitoring status (e.g., "ALERT" or "OK").
  4. Logs any events in Firestore.
  5. Provides an endpoint `/monitor_status` to return the current status to the frontend.

#### EHR PDF Generation (`app/routers/ehr_pdf.py`)

- **Functionality:**  
  Generates an Electronic Health Record (EHR) report in PDF format based on the latest transcription summary.
  
- **Flow:**  
  1. Retrieves the latest summary from Firestore.
  2. Constructs a detailed prompt for Gemini to generate an EHR report.
  3. Uses ReportLab’s Platypus module to format and style the report into a professional PDF.
  4. Saves the PDF to a temporary file and returns it as a downloadable file.


![image](https://github.com/user-attachments/assets/132a68f4-ddd9-4cc5-b048-f691d3f5eae8)

### Utility Modules

#### Google Gemini Utilities (`app/utils/gemini_utils.py`)

- **Purpose:**  
  Contains helper functions to interface with Google Gemini for generative AI tasks.
  
- **Key Points:**  
  - Centralizes the logic to call Gemini.
  - Handles both text and image inputs.
  - Manages error handling for Gemini API calls.

#### FAISS Index Utilities (`app/utils/faiss_utils.py`)

- **Purpose:**  
  Provides functionality to generate sentence embeddings and build a FAISS index from transcription summaries.
  
- **Key Points:**  
  - Uses the SentenceTransformer model to create vector embeddings.
  - Splits text into sentences.
  - Constructs an L2-based FAISS index for fast similarity search.

#### GPU Utilities (`app/utils/gpu_utils.py`)

- **Purpose:**  
  Monitors GPU memory usage to ensure efficient performance when running the Whisper model.
  
- **Key Points:**  
  - Uses PyTorch’s CUDA utilities.
  - Logs allocated and reserved memory at various stages of processing.

---

## Asynchronous Processing and Error Handling

- **Asynchronous Endpoints:**  
  Many endpoints are defined with `async def` to allow non-blocking I/O operations, especially during external API calls and file handling.
  
- **Background Tasks:**  
  The monitoring functionality runs as a background task, allowing the main API to remain responsive.
  
- **Error Handling:**  
  Try/except blocks are used throughout the code to catch exceptions, log errors, and return meaningful HTTP responses (e.g., 404 for not found, 500 for internal errors).

---

## External Integrations

- **Firebase Firestore:**  
  Acts as the persistence layer for transcription summaries, prescription details, and monitoring logs.
  
- **Google Gemini:**  
  Handles generative tasks such as speaker diarization, chat response generation, image analysis, prescription extraction, and EHR generation.
  
- **Whisper Model:**  
  Performs the heavy lifting of converting audio files to text.
  
- **FAISS:**  
  Provides rapid vector search capabilities for retrieval-augmented chat.
  
- **ESP32-CAM:**  
  Supplies the live video feed for real-time monitoring.

---

## Development and Deployment Considerations

- **Environment Management:**  
  Use a virtual environment to manage Python dependencies. Ensure that environment variables or secure vaults manage sensitive API keys and credentials.
  
- **Push Protection:**  
  Be aware of GitHub’s secret scanning; never commit sensitive files. Use a `.gitignore` file to exclude credentials.
  
- **Scalability:**  
  The modular design and asynchronous processing allow the backend to scale. Consider using production-grade servers and container orchestration (e.g., Docker, Kubernetes) for deployment.

---

## Troubleshooting & Logging

- **Error Logging:**  
  Each endpoint logs errors via print statements or logging mechanisms. These logs help in diagnosing issues.
  
- **Common Issues:**  
  - **File Format Errors:**  
    The `/transcribe` endpoint only supports certain audio formats. Update the allowed MIME types if necessary.
  - **Connectivity Issues:**  
    Ensure that external services (Firebase, Google Gemini) are reachable and properly configured.
  - **Performance Bottlenecks:**  
    Monitor GPU memory usage using the provided GPU utilities.

---

## Conclusion

The backend of VitalGenie is a robust, modular API built with FastAPI that integrates cutting-edge AI models and external services. It is designed to handle complex medical data processing tasks in real time while remaining scalable and maintainable. By separating concerns into routers, utilities, and configuration files, the project is structured for ease of development, testing, and future expansion.

For any additional questions or contributions, please refer to the project’s issue tracker or contact the maintainers.

---
