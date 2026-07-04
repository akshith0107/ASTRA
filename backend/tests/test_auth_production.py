import pytest
from fastapi.testclient import TestClient
from jose import jwt
from app.main import app
from app.core.config import settings

client = TestClient(app)

@pytest.fixture(scope="module")
def test_user():
    import uuid
    uid = str(uuid.uuid4())[:8]
    return {
        "username": f"test_op_{uid}",
        "email": f"operator_{uid}@astra.net",
        "password": "SecurePassword123!"
    }

def test_register_and_jwt_claims(test_user):
    response = client.post("/api/v1/auth/register", json=test_user)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Verify standard RFC 7519 claims
    payload = jwt.decode(
        data["access_token"], 
        settings.SECRET_KEY, 
        algorithms=[settings.ALGORITHM],
        issuer=settings.JWT_ISSUER,
        audience=settings.JWT_AUDIENCE
    )
    assert payload["sub"] == test_user["username"]
    assert "iat" in payload
    assert "nbf" in payload
    assert "exp" in payload
    assert "iss" in payload and payload["iss"] == settings.JWT_ISSUER
    assert "aud" in payload and payload["aud"] == settings.JWT_AUDIENCE
    assert "jti" in payload

def test_login_and_protected_me(test_user):
    response = client.post(
        "/api/v1/auth/login", 
        data={"username": test_user["username"], "password": test_user["password"]}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    token = data["access_token"]

    # Test protected endpoint
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["username"] == test_user["username"]
    assert me_data["email"] == test_user["email"]

def test_refresh_token_rotation_and_revocation(test_user):
    # Login to get initial tokens
    login_res = client.post(
        "/api/v1/auth/login", 
        data={"username": test_user["username"], "password": test_user["password"]}
    )
    data = login_res.json()
    old_refresh = data["refresh_token"]

    # Refresh token
    ref_res = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert ref_res.status_code == 200, ref_res.text
    ref_data = ref_res.json()
    new_refresh = ref_data["refresh_token"]
    assert new_refresh != old_refresh

    # Attempt reuse of rotated (revoked) old refresh token
    reuse_res = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert reuse_res.status_code == 401
    assert "revoked" in reuse_res.json()["detail"].lower() or "invalid" in reuse_res.json()["detail"].lower()

def test_security_headers():
    res = client.get("/")
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "default-src" in res.headers.get("Content-Security-Policy", "")

def test_logout_and_cache_revocation(test_user):
    login_res = client.post(
        "/api/v1/auth/login", 
        data={"username": test_user["username"], "password": test_user["password"]}
    )
    data = login_res.json()
    token = data["access_token"]
    refresh = data["refresh_token"]

    # Verify me works
    assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200

    # Logout
    logout_res = client.post(
        "/api/v1/auth/logout", 
        json={"refresh_token": refresh},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert logout_res.status_code == 200

    # Verify refresh token is now unusable
    ref_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert ref_res.status_code == 401
