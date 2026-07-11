from fastapi import APIRouter, HTTPException
from app.schemas.transcription import TranscriptionResponse
from app.services.profiling import analyze_text

router = APIRouter()

@router.post("/profile", response_model=TranscriptionResponse)
async def profile_text(transcription: TranscriptionResponse):
    try:
        urgency_level = analyze_text(transcription.text)
        return {"text": transcription.text, "urgency": urgency_level}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))