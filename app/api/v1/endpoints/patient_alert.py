from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict
import tempfile
import os
from app.services.transcription import transcribe_audio
from app.services.profiling import profile_text
from app.services.alerting import trigger_alert

router = APIRouter()

class PatientAlertResponse(BaseModel):
    user_id: str
    transcribed_text: str
    urgency_level: str
    tags: List[str]
    reason: str
    alert_sent: bool
    alert_results: Dict[str, bool] = {}

@router.post("/patient_alert", response_model=PatientAlertResponse)
async def patient_alert(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    file: UploadFile = File(...),
):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")

    try:
        # 1. Save audio to a cross-platform temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            temp_path = tmp.name
            tmp.write(await file.read())

        # 2. Transcribe audio
        transcribed_text = await transcribe_audio(temp_path)

        # 3. Analyze text using LLM
        profile = await profile_text(transcribed_text)
        urgency_level = profile.get("urgency", "MEDIUM")
        tags = profile.get("tags", [])
        reason = profile.get("reason", "")

        # 4. Trigger alerts asynchronously if urgency is HIGH or MEDIUM
        alert_sent = False
        alert_results = {}
        if urgency_level.upper() in ["HIGH", "MEDIUM"]:
            alert_results = trigger_alert(
                urgency_level=urgency_level,
                message=transcribed_text,
                background_tasks=background_tasks
            )
            alert_sent = any(alert_results.values())

        # 5. Clean up temp file
        os.remove(temp_path)

        # 6. Return unified response
        return PatientAlertResponse(
            user_id=user_id,
            transcribed_text=transcribed_text,
            urgency_level=urgency_level,
            tags=tags,
            reason=reason,
            alert_sent=alert_sent,
            alert_results=alert_results
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
