import logging
import httpx
from typing import Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class WebhookService:
    @staticmethod
    async def dispatch_webhook(webhook_url: str, job_data: Dict[str, Any]):
        """
        Sends an HTTP POST notification to the client's webhook endpoint when a job completes.
        """
        if not webhook_url:
            return

        payload = {
            "event": "transcription.completed",
            "job_id": job_data.get("job_id"),
            "status": job_data.get("status"),
            "data": job_data
        }

        try:
            logger.info(f"Dispatching webhook callback to: {webhook_url}")
            async with httpx.AsyncClient(timeout=settings.WEBHOOK_TIMEOUT_SECONDS) as client:
                resp = await client.post(webhook_url, json=payload)
                logger.info(f"Webhook response from {webhook_url}: {resp.status_code}")
        except Exception as e:
            logger.warning(f"Webhook delivery failed for {webhook_url}: {e}")
