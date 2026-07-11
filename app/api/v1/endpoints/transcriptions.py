from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.transcription import transcribe_audio
from app.schemas.transcription import TranscriptionResponse

router = APIRouter()

@router.post("/transcribe", response_model=TranscriptionResponse)
async def create_transcription(file: UploadFile = File(...)):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")
    
    try:
        transcription = await transcribe_audio(file)
        return TranscriptionResponse(transcribed_text=transcription)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))