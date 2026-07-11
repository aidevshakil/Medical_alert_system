# app/services/audio_service.py
from openai import AsyncOpenAI
from app.core.config import settings

# use the API key defined in `app/core/config.py` (from `.env`)
client = AsyncOpenAI(api_key=settings.API_KEY)
async def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes audio file to text using Whisper API.
    """
    with open(audio_path, "rb") as f:
        transcript =await client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    return transcript.text