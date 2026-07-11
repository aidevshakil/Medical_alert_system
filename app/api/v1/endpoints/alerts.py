from fastapi import APIRouter, HTTPException
from app.schemas.alert import AlertSchema
from app.services.alerting import trigger_alert

router = APIRouter()

@router.post("/alerts", response_model=AlertSchema)
async def send_alert(alert: AlertSchema):
    try:
        result = await trigger_alert(alert)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))