from fastapi import Header, HTTPException, status, Request
from typing import Optional
from app.config import settings
from app.database.models import ApiKeyModel


async def get_current_api_key(request: Request, x_api_key: Optional[str] = Header(None)) -> ApiKeyModel:
    """
    Validates API key from request headers. Allows Master Key or registered API keys.
    """
    db = request.app.state.db

    # In local development if no key provided, allow demo access
    if not x_api_key:
        if settings.ENVIRONMENT == "development":
            return ApiKeyModel(key="demo_dev_key", client_name="Local Developer", tier="enterprise", monthly_limit=99999)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header. Provide a valid API key to access this endpoint."
        )

    # Master Key check
    if x_api_key == settings.MASTER_API_KEY:
        return ApiKeyModel(key=settings.MASTER_API_KEY, client_name="Master Administrator", tier="enterprise", monthly_limit=99999)

    # Lookup in database
    api_key_obj = await db.get_api_key(x_api_key)
    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key."
        )

    # Check monthly quota
    if api_key_obj.used_count >= api_key_obj.monthly_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Monthly API quota exceeded for this key. Please upgrade your tier."
        )

    await db.increment_usage(x_api_key)
    return api_key_obj
