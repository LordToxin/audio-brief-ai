import pytest
import pytest_asyncio
from pathlib import Path
import httpx
from httpx import ASGITransport
from app.main import app
from app.database.db import Database
from app.config import settings


@pytest_asyncio.fixture
async def test_client(tmp_path: Path):
    test_db_path = tmp_path / "test_audio.db"
    test_db = Database(test_db_path)
    await test_db.init_tables()
    app.state.db = test_db

    # Create dummy upload directory
    settings.UPLOAD_DIR = str(tmp_path / "uploads")
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
