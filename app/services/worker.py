import logging
from pathlib import Path
from typing import Optional
from app.database.db import Database
from app.services.audio_utils import AudioUtils
from app.services.transcription import TranscriptionService
from app.services.summarizer import SummarizerService
from app.services.webhook import WebhookService

logger = logging.getLogger(__name__)


class JobWorker:
    @staticmethod
    async def process_job(
        db: Database,
        job_id: str,
        file_path: Path,
        file_size_bytes: int,
        language: str = "ru",
        webhook_url: Optional[str] = None
    ):
        """
        Background task executing the complete audio transcription and summarization workflow.
        """
        logger.info(f"Starting background job: {job_id}")
        await db.update_job_status(job_id, status="PROCESSING")

        try:
            # 1. Estimate duration
            duration = AudioUtils.estimate_duration_seconds(file_path, file_size_bytes)

            # 2. Transcribe
            transcript = await TranscriptionService.transcribe_audio(file_path, language=language)

            # 3. Summarize & Extract Intelligence
            brief = await SummarizerService.generate_brief(transcript)

            # 4. Save to Database
            action_items_dicts = [a.model_dump() for a in brief.action_items]
            await db.complete_job(
                job_id=job_id,
                duration_seconds=duration,
                transcript=transcript,
                summary=brief.summary,
                key_points=brief.key_points,
                action_items=action_items_dicts,
                sentiment=brief.sentiment,
                topics=brief.topics
            )

            logger.info(f"Job {job_id} successfully completed!")

            # 5. Dispatch Webhook
            if webhook_url:
                job_response = await db.get_job(job_id)
                if job_response:
                    await WebhookService.dispatch_webhook(webhook_url, job_response.model_dump())

        except Exception as e:
            logger.exception(f"Job {job_id} encountered an error: {e}")
            await db.update_job_status(job_id, status="FAILED", error_message=str(e))
