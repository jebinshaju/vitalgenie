import io
from PIL import Image
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.utils.gemini_utils import gemini_inference

router = APIRouter()

@router.post("/image_analysis")
async def analyze_image(file: UploadFile = File(...), prompt: str = "Describe this medical image.") -> JSONResponse:
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid format. Upload an image file.")
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading image: {e}")
    response_text = gemini_inference(prompt=prompt, image=image)
    return JSONResponse(content={"analysis": response_text})
