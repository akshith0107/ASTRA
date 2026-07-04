import pytest
import io
import wave
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_header():
    import uuid
    uid = str(uuid.uuid4())[:8]
    user_data = {
        "username": f"audio_op_{uid}",
        "email": f"audio_{uid}@astra.net",
        "password": "SecurePassword123!"
    }
    # Register user
    reg_res = client.post("/api/v1/auth/register", json=user_data)
    assert reg_res.status_code == 200
    token = reg_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def create_mock_wav(duration_seconds=1, sample_rate=16000) -> bytes:
    """Generates a valid mono 16-bit PCM WAV file in memory."""
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        # 1 second of silence
        wav_file.writeframes(b'\x00\x00' * sample_rate * duration_seconds)
    return wav_io.getvalue()

def test_unsupported_format(auth_header):
    files = {"file": ("test.txt", b"dummy content", "text/plain")}
    res = client.post("/api/v1/analyze/audio", files=files, headers=auth_header)
    assert res.status_code == 400
    assert "Unsupported file format" in res.json()["detail"]

def test_corrupted_format(auth_header):
    files = {"file": ("test.wav", b"corrupted wave header metadata", "audio/wav")}
    res = client.post("/api/v1/analyze/audio", files=files, headers=auth_header)
    assert res.status_code == 400
    assert "Corrupted or invalid audio file format" in res.json()["detail"]

def test_too_large_file(auth_header):
    # Maximum is 25MB, let's send 26MB dummy data
    large_data = b"0" * (26 * 1024 * 1024)
    files = {"file": ("test.wav", large_data, "audio/wav")}
    res = client.post("/api/v1/analyze/audio", files=files, headers=auth_header)
    assert res.status_code == 413
    assert "Audio file too large" in res.json()["detail"]

def test_valid_audio_analysis(auth_header):
    # Generates a valid wave format file
    wav_bytes = create_mock_wav(duration_seconds=2)
    files = {"file": ("test.wav", wav_bytes, "audio/wav")}
    
    # We mock or let it run (Whisper will find CapCut ffmpeg dynamically!)
    res = client.post("/api/v1/analyze/audio", files=files, headers=auth_header)
    
    # The endpoint should return a 200 AnalyzeResponse!
    assert res.status_code == 200, res.text
    data = res.json()
    assert "risk_score" in data
    assert "scam_type" in data
    assert "transcript" in data
