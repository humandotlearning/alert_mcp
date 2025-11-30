from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from .models import Alert
from .schemas import AlertCreate, AlertRead, AlertSummary

def log_alert(
    db: Session,
    provider_id: int,
    severity: str,
    window_days: int,
    message: str,
    credential_id: Optional[int] = None,
    channel: str = "ui"
) -> AlertRead:
    """
    Inserts a new row into alerts.
    Validates severity (only allow "info", "warning", "critical").
    Returns the created alert record.
    """
    if severity not in ("info", "warning", "critical"):
        raise ValueError("Severity must be one of: 'info', 'warning', 'critical'")

    alert_data = AlertCreate(
        provider_id=provider_id,
        credential_id=credential_id,
        severity=severity,
        window_days=window_days,
        message=message,
        channel=channel
    )

    db_alert = Alert(**alert_data.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return AlertRead.from_orm(db_alert)

def get_open_alerts(
    db: Session,
    provider_id: Optional[int] = None,
    severity: Optional[str] = None
) -> List[AlertRead]:
    """
    Returns alerts where resolved_at IS NULL.
    Optional filters: by provider_id, by severity.
    Sorted by severity (critical > warning > info), then by created_at desc.
    """
    query = db.query(Alert).filter(Alert.resolved_at == None)

    if provider_id is not None:
        query = query.filter(Alert.provider_id == provider_id)

    if severity is not None:
        query = query.filter(Alert.severity == severity)

    # Sorting: critical (3), warning (2), info (1)
    # We can use a CASE statement for custom sort order or mapped values.
    # A simple way in python is to fetch and sort, but doing it in SQL is better.
    # Let's map severity to int for sorting using SQLAlchemy case
    from sqlalchemy import case

    severity_order = case(
        (Alert.severity == 'critical', 3),
        (Alert.severity == 'warning', 2),
        (Alert.severity == 'info', 1),
        else_=0
    )

    query = query.order_by(severity_order.desc(), Alert.created_at.desc())

    alerts = query.all()
    return [AlertRead.from_orm(a) for a in alerts]

def mark_alert_resolved(
    db: Session,
    alert_id: int,
    resolution_note: Optional[str] = None
) -> AlertRead:
    """
    Updates resolved_at with current timestamp.
    Sets resolution_note.
    Returns the updated alert.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise ValueError(f"Alert with id {alert_id} not found")

    alert.resolved_at = datetime.utcnow()
    alert.resolution_note = resolution_note
    db.commit()
    db.refresh(alert)
    return AlertRead.from_orm(alert)

def summarize_alerts(
    db: Session,
    window_days: Optional[int] = None
) -> AlertSummary:
    """
    For a dashboard:
      - Count alerts by severity.
      - Optionally filter by alerts created in the last window_days.
    """
    query = db.query(Alert.severity, func.count(Alert.id))

    if window_days is not None:
        cutoff = datetime.utcnow() - timedelta(days=window_days)
        query = query.filter(Alert.created_at >= cutoff)

    query = query.group_by(Alert.severity)
    results = query.all()

    # results is list of (severity, count)
    counts = {row[0]: row[1] for row in results}

    # Fill missing keys with 0
    for s in ["info", "warning", "critical"]:
        if s not in counts:
            counts[s] = 0

    total = sum(counts.values())

    return AlertSummary(
        window_days=window_days,
        total_alerts=total,
        by_severity=counts
    )
