import os
import tempfile
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.config import db, whisper_model
from app.utils.gemini_utils import gemini_inference

router = APIRouter()

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)) -> JSONResponse:
    if file.content_type not in ["audio/wav", "audio/x-wav", "audio/mpeg"]:
        raise HTTPException(status_code=400, detail="Invalid format. Upload a WAV or MP3 file.")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        temp_filename = tmp.name
        tmp.write(await file.read())
    try:
        transcription_result = whisper_model.transcribe(temp_filename, language="en")
        full_transcription = transcription_result["text"].strip()
    except Exception as e:
        os.remove(temp_filename)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")
    os.remove(temp_filename)
    print("✅ Transcription Completed Successfully!")
    
    diarization_prompt = (
        "You are an expert speech analyst. Given the following transcription from a meeting, "
        "please split the transcript into segments by speaker. For each segment, if possible, "
        "provide a start time, end time, speaker label, and the corresponding transcript. "
        "If timestamps are not available, simply separate the text by speaker. "
        f"Transcription:\n{full_transcription}"
    )
    diarized_transcript = gemini_inference(diarization_prompt)
    print("🔹 Diarized Transcript from Gemini:", diarized_transcript)
    
    try:
        doc_ref = db.collection("transcription_summaries").document()
        doc_ref.set({
            "summary": diarized_transcript,
            "timestamp": datetime.utcnow()
        })
        print("🔹 Saved transcription summary to Firestore.")
    except Exception as e:
        print(f"Error saving summary to Firestore: {e}")
        
    return JSONResponse(content={"transcription": full_transcription, "diarized": diarized_transcript})
