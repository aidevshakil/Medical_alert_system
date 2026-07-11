# Voice-to-Text Profiling & Doctor Alert (medical_alert)

Short summary
- This repository implements the core AI pipeline for converting patient audio to text, profiling the transcript for urgency, and preparing alerts for doctors.
- Implemented components:
  - Transcription service using OpenAI Whisper (app/services/transcription.py).
  - Text profiling using an LLM wrapper + a small keyword analyzer (app/services/profiling.py).
- Missing / TODO:
  - Audio capture & preprocessing utilities for live recording.
  - API endpoints to fully orchestrate capture → transcribe → profile → alert (some endpoints skeletons expected but not present).
  - Alerting implementation (Twilio / SMTP / webhook) and persistence (DB models / migrations).
  - Background worker / queue for async jobs and retries.
  - Public/synthetic dataset ingestion + evaluation scripts.

Repository layout (high level)
- app/
  - services/
    - transcription.py          # Whisper async transcription
    - profiling.py              # LLM classification + simple keyword analyzer
  - core/
    - config.py                 # settings loader (reads .env)
  - api/ (expected)             # API endpoints (may be incomplete)
- tests/                        # unit tests (if present)
- Dockerfile
- requirements.txt
- .env                          # local env (gitignored)
- .gitignore

What is happening here (current flow)
1. Audio file is provided (path).
2. app/services/transcription.py calls OpenAI Whisper (AsyncOpenAI) to transcribe the file.
3. The transcribed text can be passed to:
   - profile_text(...) — an LLM-based classifier that returns structured JSON {urgency, tags, reason}; or
   - analyze_text(...) — a small keyword-based urgency heuristic.
4. Based on the urgency classification an alert should be sent — alerting code is not implemented yet and must be added (Twilio / SMTP / webhook).

Environment variables (from your .env)
- OPENAI_API_KEY — OpenAI API key used by Whisper and LLM calls.
- DATABASE_URL — Postgres connection string (if you add persistence).
- ALERT_SERVICE_URL — webhook URL to send alerts (if used).
- TRANSCRIPTION_SERVICE_URL — (not used when using OpenAI Whisper locally; kept for alternative service).
- LOG_LEVEL — logging level.
- SECRET_KEY — app secret for signing tokens.

Quick setup (macOS / local)
1. Create .env in repo root (example keys above). Do NOT commit secrets.
   - Generate SECRET_KEY: 
     - openssl rand -hex 32
     - or python3 -c "import secrets; print(secrets.token_urlsafe(48))"
2. Install dependencies:
   - python3 -m venv .venv
   - source .venv/bin/activate
   - python3 -m pip install -r requirements.txt
3. Run the app (adjust main module path if needed):
   - uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   - OR (Docker) docker build -t medical_alert . && docker run -p 8000:8000 medical_alert

How to test the implemented pieces locally
- Unit tests (if present):
  - python3 -m pip install pytest pytest-asyncio
  - pytest -q
- Manual test (transcription + profiling):
  - Place a test audio file (wav) into uploads/ or media/ (these folders are gitignored).
  - Run a short script that calls app.services.transcription.transcribe_audio(path) and then app.services.profiling.profile_text(transcript).
  - For profile_text, tests in repo may mock the LLM; running live requires OPENAI_API_KEY and network access.

Next recommended tasks (priority)
1. Implement alerting service (app/services/alerting.py) with Twilio + SMTP support and unit tests.
2. Add API endpoints that orchestrate the full flow and return structured results.
3. Add DB models and persistence to store transcripts, profiles, and alerts.
4. Add background worker (Celery + Redis) for async processing & retrying alerts.
5. Add a small synthetic/collected dataset under data/ for offline testing and metrics (WER, precision/recall).

Notes / safety
- The LLM-based profiler is a clinical triage assistant prototype. Do not deploy as a sole triage mechanism — add human-in-the-loop and audit logs.
- Keep PHI out of public repos and follow applicable regulations.
