from PIL import Image
from app.config import model

def gemini_inference(prompt: str, image: Image = None) -> str:
    """
    Calls the Gemini model with a text prompt and optional image input.
    """
    try:
        if image:
            response = model.generate_content([prompt, image], stream=False)
        else:
            response = model.generate_content(prompt, stream=False)
        response.resolve()
        return response.text
    except Exception as e:
        print(f"Gemini inference error: {e}")
        return "Error processing your request."
