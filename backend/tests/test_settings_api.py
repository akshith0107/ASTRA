import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_header():
    import uuid
    uid = str(uuid.uuid4())[:8]
    user_data = {
        "username": f"set_op_{uid}",
        "email": f"set_{uid}@astra.net",
        "password": "SecurePassword123!"
    }
    # Register user
    reg_res = client.post("/api/v1/auth/register", json=user_data)
    assert reg_res.status_code == 200
    token = reg_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}", "username": user_data["username"], "email": user_data["email"]}

def test_get_settings(auth_header):
    headers = {"Authorization": auth_header["Authorization"]}
    res = client.get("/api/v1/settings/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "min_confidence" in data
    assert "whisper_language" in data
    assert "auto_save_reports" in data

def test_update_settings(auth_header):
    headers = {"Authorization": auth_header["Authorization"]}
    update_data = {
        "whisper_language": "es",
        "min_confidence": 0.55,
        "auto_save_reports": False
    }
    res = client.put("/api/v1/settings/me", json=update_data, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["whisper_language"] == "es"
    assert data["min_confidence"] == 0.55
    assert data["auto_save_reports"] is False

def test_get_profile(auth_header):
    headers = {"Authorization": auth_header["Authorization"]}
    res = client.get("/api/v1/settings/profile", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == auth_header["username"]
    assert data["email"] == auth_header["email"]

def test_update_profile(auth_header):
    headers = {"Authorization": auth_header["Authorization"]}
    import uuid
    new_username = f"new_op_{str(uuid.uuid4())[:8]}"
    update_data = {
        "username": new_username
    }
    res = client.put("/api/v1/settings/profile", json=update_data, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == new_username
