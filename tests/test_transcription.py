from fastapi.testclient import TestClient
from app.main import app
from app.services.transcription import transcribe_audio

client = TestClient(app)

def test_transcribe_audio_success():
    audio_file = "path/to/test/audio.wav"  # Replace with a valid audio file path
    response = client.post("/api/v1/transcriptions/", files={"file": open(audio_file, "rb")})
    assert response.status_code == 200
    assert "transcription" in response.json()

def test_transcribe_audio_failure():
    response = client.post("/api/v1/transcriptions/", files={"file": None})
    assert response.status_code == 400
    assert "detail" in response.json()  # Check for appropriate error message

def test_transcribe_audio_invalid_format():
    audio_file = "path/to/test/invalid_format.txt"  # Replace with an invalid audio file path
    response = client.post("/api/v1/transcriptions/", files={"file": open(audio_file, "rb")})
    assert response.status_code == 415  # Unsupported Media Type
    assert "detail" in response.json()  # Check for appropriate error message