import uuid
import shutil
from pathlib import Path
from typing import Optional, List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
    Request,
    status
)
from app.config import settings
from app.database.models import ApiKeyModel, JobResponse
from app.middleware.auth_guard import get_current_api_key
from app.services.audio_utils import AudioUtils
from app.services.worker import JobWorker

router = APIRouter(prefix="/api/v1", tags=["Audio Transcription & Summarization"])


@router.post(
    "/transcribe",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit Audio for Transcription & Executive Brief"
)
async def submit_transcription_job(
    background_tasks: BackgroundTasks,
    request: Request,
    file: UploadFile = File(..., description="Audio file (.mp3, .wav, .m4a, .ogg, .flac)"),
    title: Optional[str] = Form(None, description="Optional meeting / call title"),
    language: str = Form("ru", description="Spoken language ISO code (e.g. ru, en)"),
    webhook_url: Optional[str] = Form(None, description="Callback URL notified on completion"),
    current_key: ApiKeyModel = Depends(get_current_api_key)
):
    """
    Uploads an audio recording and initiates asynchronous transcription,
    executive summarization, action item extraction, and webhook dispatch.
    """
    db = request.app.state.db

    # Validate file extension
    if not AudioUtils.is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format. Allowed extensions: {', '.join(AudioUtils.__module__ and ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac'])}"
        )

    job_id = f"job_{uuid.uuid4().hex[:12]}"
    clean_title = title.strip() if title else Path(file.filename).stem

    # Save audio file to storage directory
    safe_name = f"{job_id}_{file.filename}"
    file_path = settings.uploads_path / safe_name

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        await file.close()

    file_size_bytes = file_path.stat().st_size
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_bytes:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size limit of {settings.MAX_FILE_SIZE_MB}MB"
        )

    # Create job in database
    await db.create_job(
        job_id=job_id,
        api_key=current_key.key,
        title=clean_title,
        file_name=file.filename,
        file_path=str(file_path),
        file_size_bytes=file_size_bytes,
        webhook_url=webhook_url
    )

    # Enqueue background task
    background_tasks.add_task(
        JobWorker.process_job,
        db=db,
        job_id=job_id,
        file_path=file_path,
        file_size_bytes=file_size_bytes,
        language=language,
        webhook_url=webhook_url
    )

    job_obj = await db.get_job(job_id)
    return job_obj


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    summary="Get Job Status, Transcript & Brief"
)
async def get_job_status(
    job_id: str,
    request: Request,
    current_key: ApiKeyModel = Depends(get_current_api_key)
):
    """
    Polls the processing status and results of a transcription job.
    """
    db = request.app.state.db
    job = await db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    return job


@router.get(
    "/jobs",
    response_model=List[JobResponse],
    summary="List All Jobs"
)
async def list_jobs(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    current_key: ApiKeyModel = Depends(get_current_api_key)
):
    """
    Lists transcription jobs associated with the current API key.
    """
    db = request.app.state.db
    return await db.list_jobs(api_key=current_key.key, limit=limit, offset=offset)
