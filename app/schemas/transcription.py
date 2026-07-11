from pydantic import BaseModel

class TranscriptionRequest(BaseModel):
    audio_file: str

class TranscriptionResponse(BaseModel):
    transcribed_text: str
    status: str
    error: str = None