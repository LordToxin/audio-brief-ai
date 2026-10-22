import io
import pytest
import httpx
from app.config import settings
from app.services.worker import JobWorker


def create_mock_wav_bytes() -> bytes:
    """Generates a minimal valid 44-byte WAV audio buffer for testing."""
    header = bytearray(44)
    header[0:4] = b"RIFF"
    header[8:12] = b"WAVE"
    header[12:16] = b"fmt "
    header[16:20] = (16).to_bytes(4, "little")  # subchunk1 size
    header[20:22] = (1).to_bytes(2, "little")   # audio format PCM
    header[22:24] = (1).to_bytes(2, "little")   # num channels = 1
    header[24:28] = (16000).to_bytes(4, "little")  # sample rate = 16000
    header[28:32] = (32000).to_bytes(4, "little")  # byte rate = 32000
    header[32:34] = (2).to_bytes(2, "little")   # block align = 2
    header[34:36] = (16).to_bytes(2, "little")  # bits per sample = 16
    header[36:40] = b"data"
    header[40:44] = (32000).to_bytes(4, "little")  # data size (1 second)
    data = b"\x00" * 32000
    return bytes(header + data)


@pytest.mark.asyncio
async def test_transcribe_audio_upload_and_results(test_client: httpx.AsyncClient):
    headers = {"X-API-Key": settings.MASTER_API_KEY}
    wav_bytes = create_mock_wav_bytes()

    files = {"file": ("team_standup.wav", io.BytesIO(wav_bytes), "audio/wav")}
    data = {
        "title": "Weekly Engineering Sync",
        "language": "ru"
    }

    # Submit job (FastAPI BackgroundTasks processes it)
    resp = await test_client.post("/api/v1/transcribe", files=files, data=data, headers=headers)
    assert resp.status_code == 202
    job_info = resp.json()
    job_id = job_info["job_id"]
    assert job_id.startswith("job_")
    assert job_info["title"] == "Weekly Engineering Sync"

    # Poll status (already completed by background task)
    status_resp = await test_client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert status_resp.status_code == 200
    completed_job = status_resp.json()

    assert completed_job["status"] == "COMPLETED"
    assert completed_job["transcript"] is not None
    assert len(completed_job["transcript"]) > 50
    assert completed_job["summary"] is not None
    assert len(completed_job["key_points"]) >= 3
    assert len(completed_job["action_items"]) >= 2
    assert completed_job["action_items"][0]["assignee"] != ""
    assert completed_job["sentiment"] in ["Positive", "Neutral", "Constructive"]
    assert len(completed_job["topics"]) >= 2


@pytest.mark.asyncio
async def test_unsupported_file_format(test_client: httpx.AsyncClient):
    headers = {"X-API-Key": settings.MASTER_API_KEY}
    files = {"file": ("malicious_script.exe", io.BytesIO(b"binary"), "application/octet-stream")}
    resp = await test_client.post("/api/v1/transcribe", files=files, headers=headers)
    assert resp.status_code == 400
    assert "Unsupported audio format" in resp.json()["detail"]
