import io
import json
import re
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from app.config import db
from app.utils.gemini_utils import gemini_inference

router = APIRouter()

@router.post("/extract_prescription")
async def extract_prescription(
    text: str = Form(None),
    file: UploadFile = File(None)
) -> JSONResponse:
    if not text and not file:
        raise HTTPException(status_code=400, detail="Provide either conversation text or an image file for extraction.")
    
    extraction_prompt = (
        "You are an expert medical data extractor. Extract any medical prescription details from the input provided. "
        "If the input is a patient conversation, identify and extract any prescription information mentioned by the doctor. "
        "Output the details in JSON format with the following structure:\n\n"
        "{\n"
        '  "medications": [\n'
        "    {\n"
        '      "name": "<medicine name>",\n'
        '      "dosage": "<dosage information>",\n'
        '      "frequency": "<frequency of administration>",\n'
        '      "duration": "<duration if available>",\n'
        '      "notes": "<additional notes if any>"\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "If no prescription is present, return an empty medications list."
    )
    
    if text:
        extraction_input = extraction_prompt + "\n\nInput Text:\n" + text
        extraction_result = gemini_inference(extraction_input)
    else:
        try:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents)).convert("RGB")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading image: {e}")
        extraction_result = gemini_inference(prompt=extraction_prompt, image=image)
    
    print("🔹 Raw Extraction Result from Gemini:", extraction_result)
    cleaned_result = extraction_result.strip()
    cleaned_result = re.sub(r"^```(?:json)?\s*", "", cleaned_result)
    cleaned_result = re.sub(r"\s*```$", "", cleaned_result)
    try:
        prescription_data = json.loads(cleaned_result)
    except Exception as e:
        prescription_data = {"medications": []}
        print(f"Error parsing extraction result as JSON: {e}")
    
    try:
        doc_ref = db.collection("prescriptions").document()
        doc_ref.set({
            "prescription": prescription_data,
            "timestamp": datetime.utcnow(),
            "source": "text" if text else "image"
        })
        print("🔹 Saved prescription data to Firestore.")
    except Exception as e:
        print(f"Error saving prescription data to Firestore: {e}")
    
    return JSONResponse(content={"extracted_prescription": prescription_data})
