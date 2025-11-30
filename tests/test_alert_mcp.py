import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.alert_mcp.main import app, get_db
from src.alert_mcp.models import Base, Alert
from src.alert_mcp.schemas import AlertCreate

# Setup in-memory DB for tests
# We need to make sure the connection is shared if we use :memory:
# or use a file. The issue with :memory: and multiple sessions is that
# each connection gets a fresh DB unless shared cache is used or same connection.
# For FastAPI dependency injection with SessionLocal, each request gets a new session.
# If they open new connections, they might see different in-memory DBs if not careful.
# But SQLAlchemy engine usually pools connections.

# Let's try StaticPool for in-memory testing to keep data across sessions
from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def init_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

def test_log_alert(client):
    response = client.post(
        "/mcp/tools/log_alert",
        json={
            "provider_id": 1,
            "severity": "critical",
            "window_days": 30,
            "message": "Test alert",
            "channel": "ui"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["provider_id"] == 1
    assert data["severity"] == "critical"
    assert data["id"] is not None
    assert data["resolved_at"] is None

def test_log_alert_invalid_severity(client):
    response = client.post(
        "/mcp/tools/log_alert",
        json={
            "provider_id": 1,
            "severity": "super_critical",
            "window_days": 30,
            "message": "Test alert"
        }
    )
    # FastAPI/Pydantic validation returns 422 Unprocessable Entity
    assert response.status_code == 422

def test_get_open_alerts(client):
    # Create two alerts
    client.post("/mcp/tools/log_alert", json={
        "provider_id": 1, "severity": "info", "window_days": 30, "message": "Info alert"
    })
    client.post("/mcp/tools/log_alert", json={
        "provider_id": 1, "severity": "critical", "window_days": 30, "message": "Critical alert"
    })

    # Get all open alerts
    response = client.post("/mcp/tools/get_open_alerts", json={})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Check sorting: critical should be first
    assert data[0]["severity"] == "critical"
    assert data[1]["severity"] == "info"

def test_mark_alert_resolved(client):
    # Create alert
    create_res = client.post("/mcp/tools/log_alert", json={
        "provider_id": 1, "severity": "warning", "window_days": 30, "message": "Warning alert"
    })
    alert_id = create_res.json()["id"]

    # Resolve it
    response = client.post(
        "/mcp/tools/mark_alert_resolved",
        params={"alert_id": alert_id, "resolution_note": "Fixed it"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["resolved_at"] is not None
    assert data["resolution_note"] == "Fixed it"

    # Verify it's not in open alerts
    open_res = client.post("/mcp/tools/get_open_alerts", json={})
    assert len(open_res.json()) == 0

def test_summarize_alerts(client):
    client.post("/mcp/tools/log_alert", json={"provider_id": 1, "severity": "info", "window_days": 30, "message": "1"})
    client.post("/mcp/tools/log_alert", json={"provider_id": 1, "severity": "info", "window_days": 30, "message": "2"})
    client.post("/mcp/tools/log_alert", json={"provider_id": 1, "severity": "critical", "window_days": 30, "message": "3"})

    response = client.post("/mcp/tools/summarize_alerts", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["total_alerts"] == 3
    assert data["by_severity"]["info"] == 2
    assert data["by_severity"]["critical"] == 1
    assert data["by_severity"]["warning"] == 0
