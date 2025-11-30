import httpx
from typing import List, Optional, Dict, Any
from config import ALERT_API_BASE_URL
from schemas import AlertCreate, AlertRead, AlertResolution

# We'll use a synchronous client for simplicity in Gradio functions,
# but Gradio supports async too. Let's use synchronous for now as it's often easier with Gradio tools.
# Actually, httpx is great for async, but standard requests is often used.
# Let's stick to httpx but use it synchronously or asynchronously depending on how we define the tools.
# Gradio tools can be async def.

async def log_alert(
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
    # Validation logic is handled by Pydantic model implicitly if we use it,
    # but here we are constructing the payload.
    # Basic validation for severity
    if severity not in ["info", "warning", "critical"]:
        raise ValueError("Severity must be one of: info, warning, critical")

    payload = {
        "provider_id": provider_id,
        "credential_id": credential_id,
        "severity": severity,
        "window_days": window_days,
        "message": message,
        "channel": channel
    }

    async with httpx.AsyncClient(base_url=ALERT_API_BASE_URL) as client:
        try:
            response = await client.post("/alerts", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error occurred: {e.response.status_code} - {e.response.text}"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

async def get_open_alerts(
    provider_id: Optional[int] = None,
    severity: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get a list of open (unresolved) alerts.

    Args:
        provider_id: Optional filter by provider ID.
        severity: Optional filter by severity.
    """
    params = {}
    if provider_id is not None:
        params["provider_id"] = provider_id
    if severity is not None:
        params["severity"] = severity

    # Using POST /alerts/open with filters as per instructions, or GET if API supports params.
    # Instruction says: "GET or POST to /alerts/open with filters."
    # I'll try POST as it's more flexible for filters usually, or standard GET with query params.
    # Let's assume POST for filters body if complex, or GET with query params.
    # I will assume GET with query params first as it's standard for 'get', but the instruction says "GET or POST".
    # I will implement as GET with query params for now.

    async with httpx.AsyncClient(base_url=ALERT_API_BASE_URL) as client:
        try:
            response = await client.get("/alerts/open", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return [{"error": f"HTTP error: {e.response.status_code}"}]
        except Exception as e:
            return [{"error": str(e)}]

async def mark_alert_resolved(
    alert_id: int,
    resolution_note: Optional[str] = None
) -> Dict[str, Any]:
    """
    Mark an alert as resolved.

    Args:
        alert_id: The ID of the alert to resolve.
        resolution_note: A note explaining the resolution.
    """
    payload = {"resolution_note": resolution_note}

    async with httpx.AsyncClient(base_url=ALERT_API_BASE_URL) as client:
        try:
            response = await client.post(f"/alerts/{alert_id}/resolve", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e.response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

async def summarize_alerts(window_days: Optional[int] = None) -> Dict[str, int]:
    """
    Get a summary of alerts (counts by severity).

    Args:
        window_days: Optional window in days to summarize over.
    """
    payload = {}
    if window_days is not None:
        payload["window_days"] = window_days

    async with httpx.AsyncClient(base_url=ALERT_API_BASE_URL) as client:
        try:
            response = await client.post("/alerts/summary", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e.response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
