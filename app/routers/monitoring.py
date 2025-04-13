import io
import asyncio
import requests
from datetime import datetime
from PIL import Image
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.config import db
from app.utils.gemini_utils import gemini_inference

router = APIRouter()

ESP32_CAM_URL = "http://192.168.4.180/cam-hi.jpg"
ANOMALY_PROMPT = (
    "You are an expert medical safety monitor. Analyze the provided image from a patient's room and determine if there is any clear sign of abnormal behavior or an emergency (such as a fall, injury, or other critical event). Your answer must be exactly one of the following words, with no additional text:\n\n"
    "- ALERT (if there is clear, unambiguous evidence of an emergency or dangerous situation)\n"
    "- OK (if the scene appears normal or if you are not completely certain of an emergency)\n\n"
    "If there is any ambiguity or uncertainty, please return OK. Your answer must be exactly one word: either ALERT or OK."
)

# Global variable to store current monitoring status
monitoring_status = {"status": "OK", "message": "No anomaly detected."}

async def continuous_monitoring_task():
    global monitoring_status
    while True:
        try:
            response = requests.get(ESP32_CAM_URL, timeout=5)
            if response.status_code == 200:
                image_bytes = response.content
                image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                ai_result = gemini_inference(ANOMALY_PROMPT, image=image)
                print("Monitoring AI result:", ai_result)
                if ai_result.strip().upper() == "ALERT":
                    monitoring_status = {
                        "status": "ALERT",
                        "message": "Alert: Anomaly detected in patient room. Alert sent to hospital and emergency contacts."
                    }
                    try:
                        doc_ref = db.collection("monitor_events").document()
                        doc_ref.set({
                            "event": "Anomaly detected",
                            "timestamp": datetime.utcnow(),
                            "ai_result": ai_result
                        })
                        print("🔹 Anomaly event logged to Firestore.")
                        alert_ref = db.collection("doctor_alerts").document()
                        alert_ref.set({
                            "message": "Alert: Anomaly detected in patient room.",
                            "timestamp": datetime.utcnow(),
                            "details": ai_result
                        })
                        print("🔹 Dummy alert sent to doctor.")
                    except Exception as e:
                        print("Error logging anomaly/alert:", e)
                else:
                    monitoring_status = {
                        "status": "OK",
                        "message": "No anomaly detected."
                    }
            else:
                print("Failed to get image from ESP32. Status code:", response.status_code)
        except Exception as e:
            print("Error during continuous monitoring:", e)
            monitoring_status = {
                "status": "ERROR",
                "message": f"Error during monitoring: {e}"
            }
        await asyncio.sleep(3)

@router.get("/monitor_status")
async def monitor_status_endpoint():
    return JSONResponse(content=monitoring_status)

def start_monitoring():
    # This function can be called on app startup to run the monitoring task.
    asyncio.create_task(continuous_monitoring_task())
