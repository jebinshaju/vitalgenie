import tempfile
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.config import db
from app.utils.gemini_utils import gemini_inference
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER, TA_LEFT

router = APIRouter()

@router.get("/generate_ehr_pdf", response_class=FileResponse)
async def generate_ehr_pdf():
    """
    Generates an Electronic Health Record (EHR) PDF report from the latest transcription summary.
    The report is formatted using ReportLab's Platypus to produce a clean, professional layout.
    """
    # 1. Retrieve the latest transcription summary from Firestore
    try:
        docs = db.collection("transcription_summaries") \
                 .order_by("timestamp", direction="DESCENDING") \
                 .limit(1).stream()
        summary = None
        for doc in docs:
            summary = doc.to_dict().get("summary")
        if not summary:
            raise HTTPException(status_code=404, detail="No transcription summary available.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving summary: {e}")

    # 2. Build prompt to generate the EHR report
    prompt = (
        "You are a medical data specialist. Based on the following transcription summary from a patient encounter, "
        "generate a comprehensive electronic health record (EHR) report in plain text. Include the following sections: "
        "Patient Details, Medical History, Current Symptoms, Diagnoses, Medications, and Treatment Plan. "
        "Format the report for readability.\n\n"
        f"Transcription Summary:\n{summary}"
    )

    # For demo purposes, we will use a sample report. In practice, gemini_inference(prompt) would return this.
    # Generated report sample (markdown converted to plain text formatting)
    report_content = {
        "Patient Details": [
            "Name: (Unavailable in transcript)",
            "Date of Birth: (Unavailable in transcript)",
            "Medical Record Number: (Unavailable in transcript)"
        ],
        "Medical History": [
            "(Unavailable in transcript. Assume no relevant information was provided or needs to be gathered)"
        ],
        "Current Symptoms": [
            "Persistent cough for two weeks",
            "Shortness of breath (intermittent)",
            "Cough described as mostly dry, sometimes productive with mucus",
            "Wheezing"
        ],
        "Diagnoses": [
            "Possible Respiratory Infection (Based on wheezing and doctor's assessment)",
            "Possible Inflammation of the lungs (Based on wheezing and doctor's assessment)"
        ],
        "Medications": [
            "Antibiotics (Type unspecified in transcript)"
        ],
        "Treatment Plan": [
            "Prescription for antibiotics to treat potential infection.",
            "Recommendation for rest and increased fluid intake.",
            "Scheduled follow-up appointment to monitor progress.",
            "Instructions to return if fever develops or shortness of breath worsens."
        ]
    }
    
    # Optionally, you could replace the above with:
    # ehr_report = gemini_inference(prompt)
    # and then parse ehr_report to extract the sections.

    # 3. Generate PDF using ReportLab's Platypus
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(
            temp_file.name,
            pagesize=letter,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        # Define custom styles
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='CenterTitle', fontSize=18, leading=22, alignment=TA_CENTER, spaceAfter=20))
        styles.add(ParagraphStyle(name='Heading', fontSize=14, leading=18, alignment=TA_LEFT, spaceBefore=12, spaceAfter=8))
        styles.add(ParagraphStyle(name='Body', fontSize=12, leading=16, alignment=TA_LEFT, spaceAfter=6))
        
        story = []
        
        # Title
        story.append(Paragraph("Electronic Health Record (EHR) Report", styles['CenterTitle']))
        
        # For each section, add a heading and list its items
        for section, items in report_content.items():
            story.append(Paragraph(section + ":", styles['Heading']))
            for item in items:
                # Using a bullet-like symbol for clarity
                story.append(Paragraph(f"• {item}", styles['Body']))
            story.append(Spacer(1, 12))
        
        doc.build(story)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {e}")
    
    headers = {"Content-Disposition": 'attachment; filename="ehr_report.pdf"'}
    return FileResponse(temp_file.name, media_type="application/pdf", headers=headers)
