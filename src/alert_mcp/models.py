from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Using Integer directly as we might not have the providers/credentials tables in this context
    # In a full system with shared models, these would be ForeignKey("providers.id")
    provider_id: Mapped[int] = mapped_column(Integer, nullable=False)
    credential_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    severity: Mapped[str] = mapped_column(String, nullable=False) # "info", "warning", "critical"
    window_days: Mapped[int] = mapped_column(Integer, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[str] = mapped_column(String, default="ui")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolution_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"<Alert(id={self.id}, severity='{self.severity}', message='{self.message}')>"
