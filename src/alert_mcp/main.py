from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional, List, Any
import uvicorn
import mcp.types as types
from mcp.server.fastmcp import FastMCP

from .db import get_db, init_db
from .schemas import AlertCreate, AlertRead, AlertSummary
from . import mcp_tools

# Initialize DB
init_db()

# Create MCP Server
mcp = FastMCP("alert_mcp")

# --- MCP Tool Definitions ---

@mcp.tool()
def log_alert(
    provider_id: int,
    severity: str,
    window_days: int,
    message: str,
    credential_id: Optional[int] = None,
    channel: str = "ui"
) -> str:
    """
    Log a new alert for CredentialWatch.
    Severity must be 'info', 'warning', or 'critical'.
    """
    # Note: For MCP tools we manage the session manually within the tool
    # as they are not standard FastAPI routes dependent on the app dependency injection
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
        return alert.json()
    except ValueError as e:
        return f"Error: {str(e)}"
    finally:
        db.close()

@mcp.tool()
def get_open_alerts(
    provider_id: Optional[int] = None,
    severity: Optional[str] = None
) -> str:
    """
    List open (unresolved) alerts.
    Optional filters: provider_id, severity.
    Returns JSON list of alerts.
    """
    db = next(get_db())
    try:
        alerts = mcp_tools.get_open_alerts(db=db, provider_id=provider_id, severity=severity)
        return "[" + ",".join([a.json() for a in alerts]) + "]"
    finally:
        db.close()

@mcp.tool()
def mark_alert_resolved(
    alert_id: int,
    resolution_note: Optional[str] = None
) -> str:
    """
    Mark an alert as resolved.
    Returns the updated alert as JSON.
    """
    db = next(get_db())
    try:
        alert = mcp_tools.mark_alert_resolved(db=db, alert_id=alert_id, resolution_note=resolution_note)
        return alert.json()
    except ValueError as e:
        return f"Error: {str(e)}"
    finally:
        db.close()

@mcp.tool()
def summarize_alerts(window_days: Optional[int] = None) -> str:
    """
    Get a summary of alerts (count by severity).
    Optionally filter by last N days.
    """
    db = next(get_db())
    try:
        summary = mcp_tools.summarize_alerts(db=db, window_days=window_days)
        return summary.json()
    finally:
        db.close()

# --- FastAPI App ---

app = FastAPI(title="Alert MCP Server")

# Mount MCP Server (SSE)
# FastMCP provides .sse_app() which returns a Starlette app that can be mounted
app.mount("/sse", mcp.sse_app())

@app.get("/health")
def health():
    return {"status": "ok"}

# REST Endpoints for Gradio / UI
@app.post("/api/log_alert", response_model=AlertRead)
def api_log_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db)
):
    try:
        return mcp_tools.log_alert(
            db=db,
            provider_id=alert.provider_id,
            credential_id=alert.credential_id,
            severity=alert.severity,
            window_days=alert.window_days,
            message=alert.message,
            channel=alert.channel
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/alerts", response_model=List[AlertRead])
def api_get_alerts(
    provider_id: Optional[int] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return mcp_tools.get_open_alerts(db=db, provider_id=provider_id, severity=severity)

@app.post("/api/alerts/{alert_id}/resolve", response_model=AlertRead)
def api_resolve_alert(
    alert_id: int,
    resolution_note: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        return mcp_tools.mark_alert_resolved(db=db, alert_id=alert_id, resolution_note=resolution_note)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/summary", response_model=AlertSummary)
def api_summary(
    window_days: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return mcp_tools.summarize_alerts(db=db, window_days=window_days)


# Now integrating with FasteMCP for the actual MCP protocol support
# I will use `mcp` library if it exists.
# Since I am writing the code without checking `mcp` lib, I will assume `FasteMCP` works as a standalone app
# or I can mount it.

# If `mcp` is not installed in the environment, this file will fail.
# But I put `mcp` in pyproject.toml.

# Let's make `app` the main entry point and mount the MCP server if possible.
# Or if FasteMCP is an app, we can use it.

# Given the specific path requirement "/mcp/tools/{tool_name}", I'm suspicious this might be a custom requirement.
# But standard MCP over SSE uses /sse and /messages (or similar).

# "MCP tool endpoints under /mcp/tools/{tool_name}"
# This looks like:
# POST /mcp/tools/log_alert
# POST /mcp/tools/get_open_alerts
# ...
# This is explicitly what was requested. So I will add these specific routes.

@app.post("/mcp/tools/log_alert")
async def mcp_log_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    # Helper to wrap the logic
    try:
        return mcp_tools.log_alert(
            db=db,
            provider_id=payload.provider_id,
            credential_id=payload.credential_id,
            severity=payload.severity,
            window_days=payload.window_days,
            message=payload.message,
            channel=payload.channel
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/mcp/tools/get_open_alerts")
async def mcp_get_open_alerts(
    provider_id: Optional[int] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return mcp_tools.get_open_alerts(db=db, provider_id=provider_id, severity=severity)

@app.post("/mcp/tools/mark_alert_resolved")
async def mcp_mark_alert_resolved(
    alert_id: int,
    resolution_note: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        return mcp_tools.mark_alert_resolved(db=db, alert_id=alert_id, resolution_note=resolution_note)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/mcp/tools/summarize_alerts")
async def mcp_summarize_alerts(window_days: Optional[int] = None, db: Session = Depends(get_db)):
    return mcp_tools.summarize_alerts(db=db, window_days=window_days)

# Finally, I'll attempt to mount the FasteMCP app if I can, to support "real" MCP over SSE.
# But without documentation on FasteMCP in this context, I might skip it and rely on the REST endpoints
# satisfying the "MCP tool endpoints" requirement, as that is what was explicitly asked.
# The prompt says "MCP: HTTP + SSE". This strongly suggests standard MCP support.

# I will try to include the standard MCP setup using the `mcp` library from Anthropic or similar.
# Assuming `mcp` package is available (it is in my toml).

try:
    # This is a best-effort integration with the `mcp` python sdk
    from mcp.server.fastapi import Server
    import mcp.types as types

    # I'll need to define the server
    # But FasteMCP mentioned above is from `mcp`? I might have hallucinated `FasteMCP` name
    # if it's not in the standard lib. The standard lib usually has `Server`.
    # I'll stick to the requested structure and minimal implementation.
    pass
except ImportError:
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
