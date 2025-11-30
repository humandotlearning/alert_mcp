import json
from typing import List, Optional, Dict, Any
from src.alert_mcp.db import get_db
from src.alert_mcp import mcp_tools

# We use synchronous calls directly to the database logic
# This avoids the need for a separate backend server process in the Space.

def log_alert(
    provider_id: int,
    severity: str,
    window_days: int,
    message: str,
    credential_id: Optional[int] = None,
    channel: Optional[str] = "ui"
) -> Dict[str, Any]:
    """
    Log a new alert in the system.

    Args:
        provider_id: The ID of the provider.
        severity: One of "info", "warning", "critical".
        window_days: The window in days.
        message: The alert message.
        credential_id: Optional credential ID.
        channel: Notification channel (default: "ui").
    """
    db = next(get_db())
    try:
        alert = mcp_tools.log_alert(
            db=db,
            provider_id=provider_id,
            credential_id=credential_id,
            severity=severity,
            window_days=window_days,
            message=message,
            channel=channel
        )
        return alert.model_dump(mode='json')
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    finally:
        db.close()

def get_open_alerts(
    provider_id: Optional[int] = None,
    severity: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get a list of open (unresolved) alerts.

    Args:
        provider_id: Optional filter by provider ID.
        severity: Optional filter by severity.
    """
    db = next(get_db())
    try:
        alerts = mcp_tools.get_open_alerts(db=db, provider_id=provider_id, severity=severity)
        return [a.model_dump(mode='json') for a in alerts]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        db.close()

def mark_alert_resolved(
    alert_id: int,
    resolution_note: Optional[str] = None
) -> Dict[str, Any]:
    """
    Mark an alert as resolved.

    Args:
        alert_id: The ID of the alert to resolve.
        resolution_note: A note explaining the resolution.
    """
    db = next(get_db())
    try:
        alert = mcp_tools.mark_alert_resolved(db=db, alert_id=alert_id, resolution_note=resolution_note)
        return alert.model_dump(mode='json')
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

def summarize_alerts(window_days: Optional[int] = None) -> Dict[str, Any]:
    """
    Get a summary of alerts (counts by severity).

    Args:
        window_days: Optional window in days to summarize over.
    """
    db = next(get_db())
    try:
        summary = mcp_tools.summarize_alerts(db=db, window_days=window_days)
        return summary.model_dump(mode='json')
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()
