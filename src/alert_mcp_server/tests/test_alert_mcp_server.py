import pytest
from unittest.mock import MagicMock, patch
from src.alert_mcp_server.tools import log_alert, get_open_alerts, mark_alert_resolved, summarize_alerts

@pytest.fixture
def mock_db_session():
    with patch("src.alert_mcp_server.tools.get_db") as mock_get_db:
        mock_session = MagicMock()
        mock_get_db.return_value = iter([mock_session])
        yield mock_session

def test_log_alert(mock_db_session):
    mock_alert_read = MagicMock()
    # Mock model_dump return value
    mock_alert_read.model_dump.return_value = {"id": 1, "provider_id": 1, "severity": "info", "message": "Test alert"}

    with patch("src.alert_mcp.mcp_tools.log_alert", return_value=mock_alert_read) as mock_log:
        result = log_alert(
            provider_id=1,
            severity="info",
            window_days=30,
            message="Test alert"
        )

        assert result["id"] == 1
        mock_log.assert_called_once()
        # Verify model_dump was called with mode='json'
        mock_alert_read.model_dump.assert_called_with(mode='json')

def test_get_open_alerts(mock_db_session):
    mock_alert_read = MagicMock()
    mock_alert_read.model_dump.return_value = {"id": 1, "provider_id": 1, "severity": "critical"}

    with patch("src.alert_mcp.mcp_tools.get_open_alerts", return_value=[mock_alert_read]) as mock_get:
        result = get_open_alerts(provider_id=1)

        assert len(result) == 1
        assert result[0]["id"] == 1
        mock_get.assert_called_once()
        mock_alert_read.model_dump.assert_called_with(mode='json')

def test_mark_alert_resolved(mock_db_session):
    mock_alert_read = MagicMock()
    mock_alert_read.model_dump.return_value = {"id": 1, "resolved_at": "2023-10-27"}

    with patch("src.alert_mcp.mcp_tools.mark_alert_resolved", return_value=mock_alert_read) as mock_mark:
        result = mark_alert_resolved(alert_id=1, resolution_note="Fixed")

        assert result["id"] == 1
        mock_mark.assert_called_once()
        mock_alert_read.model_dump.assert_called_with(mode='json')

def test_summarize_alerts(mock_db_session):
    mock_summary = MagicMock()
    mock_summary.model_dump.return_value = {"total_alerts": 10, "by_severity": {"info": 5}}

    with patch("src.alert_mcp.mcp_tools.summarize_alerts", return_value=mock_summary) as mock_sum:
        result = summarize_alerts(window_days=7)

        assert result["total_alerts"] == 10
        mock_sum.assert_called_once()
        mock_summary.model_dump.assert_called_with(mode='json')
