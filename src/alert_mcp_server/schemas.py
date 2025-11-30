from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class AlertCreate(BaseModel):
    provider_id: int
    credential_id: Optional[int] = None
    severity: Literal["info", "warning", "critical"]
    window_days: int
    message: str
    channel: Optional[str] = "ui"

class AlertRead(BaseModel):
    id: int
    provider_id: int
    credential_id: Optional[int] = None
    severity: str
    window_days: int
    message: str
    channel: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_note: Optional[str] = None

class AlertResolution(BaseModel):
    resolution_note: Optional[str] = None

class AlertSummary(BaseModel):
    severity_counts: dict[str, int]
