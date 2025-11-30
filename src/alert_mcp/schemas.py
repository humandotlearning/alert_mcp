from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, validator

class AlertBase(BaseModel):
    provider_id: int
    credential_id: Optional[int] = None
    severity: Literal["info", "warning", "critical"]
    window_days: int
    message: str
    channel: str = "ui"

class AlertCreate(AlertBase):
    pass

class AlertRead(AlertBase):
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_note: Optional[str] = None

    class Config:
        from_attributes = True

class AlertSummary(BaseModel):
    window_days: Optional[int]
    total_alerts: int
    by_severity: dict[str, int]
