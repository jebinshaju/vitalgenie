import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.routers import transcribe, rag_chat, image_analysis, prescription, monitoring, ehr_pdf

app = FastAPI(
    title="VitalGenie",
    description=(
        "Upload an audio file for transcription. The entire audio is transcribed with Whisper, "
        "then Google Gemini is used to perform speaker diarization on the transcript. The resulting diarized transcript is saved to Firestore. "
        "Use the /rag_chat endpoint for retrieval-augmented questions, /image_analysis for image analysis, "
        "and /extract_prescription to extract prescription details from a conversation or a prescription image."
    ),
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from submodules
app.include_router(transcribe.router)
app.include_router(rag_chat.router)
app.include_router(image_analysis.router)
app.include_router(prescription.router)
app.include_router(monitoring.router)
app.include_router(ehr_pdf.router)


@app.get("/")
async def root():
    return {"message": "Welcome to VitalGenie!"}

@app.on_event("startup")
async def startup_event():
    monitoring.start_monitoring()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
