import pytest
import httpx
from app.config import settings


@pytest.mark.asyncio
async def test_health_endpoint(test_client: httpx.AsyncClient):
    resp = await test_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "AudioBrief AI API" in data["service"]


@pytest.mark.asyncio
async def test_generate_and_list_api_keys(test_client: httpx.AsyncClient):
    # Master key auth
    headers = {"X-API-Key": settings.MASTER_API_KEY}

    req_data = {
        "client_name": "SaaS Partner Corp",
        "tier": "enterprise",
        "monthly_limit": 1000
    }
    resp = await test_client.post("/api/v1/auth/keys", json=req_data, headers=headers)
    assert resp.status_code == 201
    key_info = resp.json()
    assert "ab_enterprise_" in key_info["key"]
    assert key_info["client_name"] == "SaaS Partner Corp"

    # List keys
    list_resp = await test_client.get("/api/v1/auth/keys", headers=headers)
    assert list_resp.status_code == 200
    keys = list_resp.json()
    assert any(k["key"] == key_info["key"] for k in keys)


@pytest.mark.asyncio
async def test_invalid_api_key_rejected(test_client: httpx.AsyncClient):
    headers = {"X-API-Key": "invalid_fake_key_12345"}
    resp = await test_client.get("/api/v1/jobs", headers=headers)
    assert resp.status_code == 401
