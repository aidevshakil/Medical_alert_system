from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import transcriptions, profiling, alerts, patient_alert

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patient_alert.router, prefix="/api/v1/patient_alert", tags=["patient_alert"])

app.include_router(transcriptions.router, prefix="/api/v1/transcriptions", tags=["transcriptions"])
app.include_router(profiling.router, prefix="/api/v1/profiling", tags=["profiling"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Voice-to-Text Profiling and Alert System"}