from fastapi import FastAPI
from app.services.alerting import trigger_alert

def test_trigger_alert(monkeypatch):
    def mock_trigger_alert(urgency_level, message):
        return {"status": "success", "urgency_level": urgency_level, "message": message}

    monkeypatch.setattr(trigger_alert, "trigger_alert", mock_trigger_alert)

    response = trigger_alert("high", "Patient requires immediate attention.")
    assert response["status"] == "success"
    assert response["urgency_level"] == "high"
    assert response["message"] == "Patient requires immediate attention."

def test_trigger_alert_failure(monkeypatch):
    def mock_trigger_alert(urgency_level, message):
        raise Exception("Alert service unavailable")

    monkeypatch.setattr(trigger_alert, "trigger_alert", mock_trigger_alert)

    try:
        trigger_alert("low", "Routine check-up needed.")
    except Exception as e:
        assert str(e) == "Alert service unavailable"