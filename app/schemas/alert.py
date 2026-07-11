
from pydantic import BaseModel
from typing import Optional

class AlertBase(BaseModel):
    patient_id: str
    urgency_level: str
    message: str

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: int

    class Config:
        orm_mode = True

# Alias
AlertSchema = Alert
