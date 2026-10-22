from fastapi import APIRouter
from app import __version__
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "AudioBrief AI API",
        "version": __version__,
        "environment": settings.ENVIRONMENT
    }
