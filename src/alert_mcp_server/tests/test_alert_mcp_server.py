
import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch
from src.alert_mcp_server.tools import log_alert, get_open_alerts, mark_alert_resolved, summarize_alerts

@pytest.mark.asyncio
async def test_log_alert():
    mock_response = {
        "id": 1,
        "provider_id": 1,
        "severity": "info",
        "message": "Test alert",
        "created_at": "2023-10-27T10:00:00"
    }

    # We use new_callable=AsyncMock for the client.post method because it is awaited.
    # However, the return value (the response object) should be a synchronous Mock (MagicMock)
    # because methods like .json() and .raise_for_status() are synchronous on the Response object.
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None

        mock_post.return_value = mock_response_obj

        result = await log_alert(
            provider_id=1,
            severity="info",
            window_days=30,
            message="Test alert"
        )

        assert result == mock_response
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["provider_id"] == 1
        assert kwargs["json"]["severity"] == "info"

@pytest.mark.asyncio
async def test_get_open_alerts():
    mock_response = [
        {
            "id": 1,
            "provider_id": 1,
            "severity": "critical",
            "message": "Critical alert",
            "created_at": "2023-10-27T10:00:00"
        }
    ]

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None

        mock_get.return_value = mock_response_obj

        result = await get_open_alerts(provider_id=1)

        assert result == mock_response
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["provider_id"] == 1

@pytest.mark.asyncio
async def test_mark_alert_resolved():
    mock_response = {
        "id": 1,
        "resolved_at": "2023-10-27T12:00:00",
        "resolution_note": "Fixed"
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None

        mock_post.return_value = mock_response_obj

        result = await mark_alert_resolved(alert_id=1, resolution_note="Fixed")

        assert result == mock_response
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_summarize_alerts():
    mock_response = {"info": 5, "warning": 2, "critical": 1}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None

        mock_post.return_value = mock_response_obj

        result = await summarize_alerts(window_days=7)

        assert result == mock_response
        mock_post.assert_called_once()
