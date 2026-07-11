from fastapi import BackgroundTasks
from app.services.transcription import transcribe_audio
from app.services.profiling import analyze_text
from app.services.alerting import trigger_alert

def process_audio(audio_file: str, background_tasks: BackgroundTasks):
    # Step 1: Transcribe audio
    transcribed_text = transcribe_audio(audio_file)
    
    # Step 2: Profile the transcribed text
    urgency_level = analyze_text(transcribed_text)
    
    # Step 3: Send alert if necessary
    if urgency_level == "high":
        background_tasks.add_task(trigger_alert, transcribed_text)