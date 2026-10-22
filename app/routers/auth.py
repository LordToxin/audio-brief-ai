import secrets
from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import List
from app.database.models import ApiKeyModel, CreateApiKeyRequest
from app.middleware.auth_guard import get_current_api_key

router = APIRouter(prefix="/api/v1/auth", tags=["API Keys & Monetization"])


@router.post("/keys", response_model=ApiKeyModel, status_code=status.HTTP_201_CREATED)
async def generate_api_key(
    req: CreateApiKeyRequest,
    request: Request,
    current_key: ApiKeyModel = Depends(get_current_api_key)
):
    """
    Generates a new API Key with assigned tier and monthly transcription quota.
    """
    db = request.app.state.db
    new_key_str = f"ab_{req.tier}_{secrets.token_urlsafe(24)}"

    api_key_obj = await db.create_api_key(
        key=new_key_str,
        client_name=req.client_name,
        tier=req.tier,
        monthly_limit=req.monthly_limit
    )
    return api_key_obj


@router.get("/keys", response_model=List[ApiKeyModel])
async def list_api_keys(
    request: Request,
    current_key: ApiKeyModel = Depends(get_current_api_key)
):
    """
    Lists all provisioned API keys.
    """
    db = request.app.state.db
    return await db.list_api_keys()
