from fastapi import BackgroundTasks
from typing import Any, Dict, List
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
import asyncio
from typing import Optional, List, Dict, Any
import smtplib
from email.message import EmailMessage
import httpx

from app.core import config

settings = config.settings

# Optional import for Twilio — only used if configured
try:
    from twilio.rest import Client as TwilioClient
except Exception:
    TwilioClient = None


async def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Send an email alert using SMTP. Runs blocking smtplib in a threadpool.
    Returns True on success, False on failure.
    """
    def _send():
        msg = EmailMessage()
        msg["From"] = getattr(settings, "ALERT_FROM_EMAIL", getattr(settings, "SMTP_USER", "no-reply@example.com"))
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        host = getattr(settings, "SMTP_HOST", None)
        port = int(getattr(settings, "SMTP_PORT", 587))
        user = getattr(settings, "SMTP_USER", None)
        password = getattr(settings, "SMTP_PASSWORD", None)

        if not host:
            raise RuntimeError("SMTP_HOST not configured")

        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=10)
        else:
            server = smtplib.SMTP(host, port, timeout=10)
            server.starttls()
        if user and password:
            server.login(user, password)
        server.send_message(msg)
        server.quit()
        return True

    try:
        return await asyncio.to_thread(_send)
    except Exception:
        return False


async def send_webhook(url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> bool:
    """
    Send a JSON POST to a webhook URL. Returns True if HTTP status < 400.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers or {})
            return resp.status_code < 400
    except Exception:
        return False


async def send_sms(phones: List[str], body: str) -> bool:
    """
    Send SMS messages using Twilio if configured. Runs Twilio client in threadpool.
    Returns True if all sends appear successful (best-effort).
    """
    account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
    from_number = getattr(settings, "TWILIO_FROM_NUMBER", None)

    if not (account_sid and auth_token and from_number and TwilioClient):
        # Twilio not configured or library missing
        return False

    def _send_all():
        client = TwilioClient(account_sid, auth_token)
        for to in phones:
            client.messages.create(body=body, from_=from_number, to=to)
        return True

    try:
        return await asyncio.to_thread(_send_all)
    except Exception:
        return False


def trigger_alert(
    urgency_level: str,
    message: str,
    doctor_emails: Optional[List[str]] = None,
    doctor_phones: Optional[List[str]] = None,
    doctor_webhooks: Optional[List[str]] = None,
    background_tasks=None,
) -> Dict[str, bool]:
    """
    Trigger alerts based on urgency.
    - urgency_level: "high" | "medium" | "low"
    - message: alert body
    - doctor_emails: list of recipient emails
    - doctor_phones: list of phone numbers for SMS
    - doctor_webhooks: list of webhook URLs to POST to
    - background_tasks: optional FastAPI BackgroundTasks instance; when present tasks are scheduled
    Returns dict with delivery attempts results (best-effort, may be False if not configured).
    """
    results = {"email": False, "sms": False, "webhook": False}

    async def _do_email_all(emails: List[str]) -> bool:
        ok = True
        for e in emails:
            if not await send_email(e, f"[ALERT] Urgency: {urgency_level.upper()}", message):
                ok = False
        return ok

    async def _do_sms_all(phones: List[str]) -> bool:
        return await send_sms(phones, message)

    async def _do_webhook_all(webhooks: List[str]) -> bool:
        ok = True
        for w in webhooks:
            if not await send_webhook(w, {"message": message, "urgency": urgency_level}):
                ok = False
        return ok

    should_send_email = bool(doctor_emails)
    should_send_sms = bool(doctor_phones)
    should_send_webhook = bool(doctor_webhooks) or bool(getattr(settings, "ALERT_SERVICE_URL", None))

    # include default configured endpoints if not provided
    if not doctor_webhooks and getattr(settings, "ALERT_SERVICE_URL", None):
        doctor_webhooks = [getattr(settings, "ALERT_SERVICE_URL")]

    # For high urgency: SMS + email + webhook; medium: email + webhook; low: none
    if urgency_level.lower() == "high":
        if should_send_sms:
            if background_tasks:
                background_tasks.add_task(_do_sms_all, doctor_phones)
                results["sms"] = True
            else:
                results["sms"] = asyncio.run(_do_sms_all(doctor_phones))
        if should_send_email:
            if background_tasks:
                background_tasks.add_task(_do_email_all, doctor_emails)
                results["email"] = True
            else:
                results["email"] = asyncio.run(_do_email_all(doctor_emails))
        if should_send_webhook:
            if background_tasks:
                background_tasks.add_task(_do_webhook_all, doctor_webhooks)
                results["webhook"] = True
            else:
                results["webhook"] = asyncio.run(_do_webhook_all(doctor_webhooks))
    elif urgency_level.lower() == "medium":
        if should_send_email:
            if background_tasks:
                background_tasks.add_task(_do_email_all, doctor_emails)
                results["email"] = True
            else:
                results["email"] = asyncio.run(_do_email_all(doctor_emails))
        if should_send_webhook:
            if background_tasks:
                background_tasks.add_task(_do_webhook_all, doctor_webhooks)
                results["webhook"] = True
            else:
                results["webhook"] = asyncio.run(_do_webhook_all(doctor_webhooks))
    else:
        # low urgency: no automatic alerts by default
        pass

    return results