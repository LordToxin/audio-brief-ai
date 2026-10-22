import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import __version__
from app.config import settings
from app.database.db import Database
from app.routers import health, auth, transcribe

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("audio_brief")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing AudioBrief AI database and services...")
    db = Database(settings.db_path)
    await db.init_tables()
    app.state.db = db
    yield
    logger.info("Shutting down AudioBrief AI...")


app = FastAPI(
    title="AudioBrief AI - Transcription & Executive Summarizer API",
    description=(
        "Production-ready Micro-SaaS API for automatic speech-to-text transcription, "
        "executive summarization, action items extraction, and webhook synchronization."
    ),
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(transcribe.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
