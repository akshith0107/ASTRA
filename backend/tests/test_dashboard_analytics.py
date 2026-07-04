import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_header():
    import uuid
    uid = str(uuid.uuid4())[:8]
    user_data = {
        "username": f"dash_op_{uid}",
        "email": f"dash_{uid}@astra.net",
        "password": "SecurePassword123!"
    }
    # Register user
    reg_res = client.post("/api/v1/auth/register", json=user_data)
    assert reg_res.status_code == 200
    token = reg_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_dashboard_stats_endpoint(auth_header):
    # Test default
    res = client.get("/api/v1/dashboard/stats", headers=auth_header)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "system_status" in data
    assert "total_reports" in data
    assert "critical_alerts" in data
    assert "active_campaigns" in data
    assert "detection_rate" in data
    assert "timeline_trends" in data
    assert "threat_distribution" in data
    assert "risk_distribution" in data
    assert "heatmap" in data
    assert "quick_insights" in data
    assert "network_summary" in data
    assert "system_health" in data
    assert "ai_models" in data
    assert "performance" in data
    assert "live_activity" in data

def test_dashboard_stats_filtering(auth_header):
    # Test with valid parameters
    res = client.get(
        "/api/v1/dashboard/stats?timeframe=24h&source_type=text&risk_level=critical", 
        headers=auth_header
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_reports"] >= 0

def test_dashboard_reports_endpoint(auth_header):
    res = client.get("/api/v1/dashboard/reports?limit=5", headers=auth_header)
    assert res.status_code == 200
    reports = res.json()
    assert isinstance(reports, list)
    if len(reports) > 0:
        assert "risk_score" in reports[0]
        assert "risk_level" in reports[0]
        assert "scam_type" in reports[0]
        assert "processing_time" in reports[0]
