import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional, Dict, Any
import aiosqlite
from app.database.models import ApiKeyModel, JobResponse, ActionItem

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)

    @asynccontextmanager
    async def connect(self):
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            await conn.close()

    async def init_tables(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        async with self.connect() as conn:
            await conn.executescript("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                client_name TEXT NOT NULL,
                tier TEXT NOT NULL DEFAULT 'pro',
                monthly_limit INTEGER NOT NULL DEFAULT 500,
                used_count INTEGER NOT NULL DEFAULT 0,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                api_key TEXT NOT NULL,
                title TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size_bytes INTEGER NOT NULL,
                duration_seconds REAL DEFAULT 0.0,
                status TEXT NOT NULL DEFAULT 'PENDING',
                transcript TEXT,
                summary TEXT,
                key_points_json TEXT,
                action_items_json TEXT,
                sentiment TEXT,
                topics_json TEXT,
                webhook_url TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_jobs_api_key ON jobs(api_key, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_api_keys_lookup ON api_keys(key, is_active);
            """)
            await conn.commit()
            logger.info("AudioBrief AI database initialized.")

    # --- API Keys ---
    async def get_api_key(self, key: str) -> Optional[ApiKeyModel]:
        async with self.connect() as conn:
            async with conn.execute("SELECT * FROM api_keys WHERE key = ? AND is_active = 1", (key,)) as cur:
                row = await cur.fetchone()
                return ApiKeyModel(**dict(row)) if row else None

    async def create_api_key(self, key: str, client_name: str, tier: str = "pro", monthly_limit: int = 500) -> ApiKeyModel:
        async with self.connect() as conn:
            cur = await conn.execute(
                "INSERT INTO api_keys (key, client_name, tier, monthly_limit, used_count, is_active) VALUES (?, ?, ?, ?, 0, 1)",
                (key, client_name, tier, monthly_limit)
            )
            await conn.commit()
            return ApiKeyModel(id=cur.lastrowid, key=key, client_name=client_name, tier=tier, monthly_limit=monthly_limit)

    async def increment_usage(self, key: str):
        async with self.connect() as conn:
            await conn.execute("UPDATE api_keys SET used_count = used_count + 1 WHERE key = ?", (key,))
            await conn.commit()

    async def list_api_keys(self) -> List[ApiKeyModel]:
        async with self.connect() as conn:
            async with conn.execute("SELECT * FROM api_keys ORDER BY id DESC") as cur:
                rows = await cur.fetchall()
                return [ApiKeyModel(**dict(r)) for r in rows]

    # --- Jobs ---
    async def create_job(
        self,
        job_id: str,
        api_key: str,
        title: str,
        file_name: str,
        file_path: str,
        file_size_bytes: int,
        webhook_url: Optional[str] = None
    ):
        async with self.connect() as conn:
            await conn.execute(
                """
                INSERT INTO jobs (job_id, api_key, title, file_name, file_path, file_size_bytes, status, webhook_url)
                VALUES (?, ?, ?, ?, ?, ?, 'PENDING', ?)
                """,
                (job_id, api_key, title, file_name, file_path, file_size_bytes, webhook_url)
            )
            await conn.commit()

    async def update_job_status(self, job_id: str, status: str, error_message: Optional[str] = None):
        async with self.connect() as conn:
            await conn.execute(
                "UPDATE jobs SET status = ?, error_message = ? WHERE job_id = ?",
                (status, error_message, job_id)
            )
            await conn.commit()

    async def complete_job(
        self,
        job_id: str,
        duration_seconds: float,
        transcript: str,
        summary: str,
        key_points: List[str],
        action_items: List[Dict[str, Any]],
        sentiment: str,
        topics: List[str]
    ):
        async with self.connect() as conn:
            await conn.execute(
                """
                UPDATE jobs SET
                    status = 'COMPLETED',
                    duration_seconds = ?,
                    transcript = ?,
                    summary = ?,
                    key_points_json = ?,
                    action_items_json = ?,
                    sentiment = ?,
                    topics_json = ?,
                    completed_at = CURRENT_TIMESTAMP
                WHERE job_id = ?
                """,
                (
                    duration_seconds,
                    transcript,
                    summary,
                    json.dumps(key_points, ensure_ascii=False),
                    json.dumps(action_items, ensure_ascii=False),
                    sentiment,
                    json.dumps(topics, ensure_ascii=False),
                    job_id
                )
            )
            await conn.commit()

    async def get_job(self, job_id: str) -> Optional[JobResponse]:
        async with self.connect() as conn:
            async with conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)) as cur:
                row = await cur.fetchone()
                if not row:
                    return None
                d = dict(row)

                # Parse JSON fields
                key_points = json.loads(d["key_points_json"]) if d.get("key_points_json") else None
                raw_actions = json.loads(d["action_items_json"]) if d.get("action_items_json") else None
                action_items = [ActionItem(**a) for a in raw_actions] if raw_actions else None
                topics = json.loads(d["topics_json"]) if d.get("topics_json") else None

                return JobResponse(
                    job_id=d["job_id"],
                    title=d["title"],
                    status=d["status"],
                    file_name=d["file_name"],
                    file_size_bytes=d["file_size_bytes"],
                    duration_seconds=d.get("duration_seconds") or 0.0,
                    transcript=d.get("transcript"),
                    summary=d.get("summary"),
                    key_points=key_points,
                    action_items=action_items,
                    sentiment=d.get("sentiment"),
                    topics=topics,
                    error=d.get("error_message"),
                    created_at=str(d.get("created_at")),
                    completed_at=str(d.get("completed_at")) if d.get("completed_at") else None
                )

    async def list_jobs(self, api_key: str, limit: int = 50, offset: int = 0) -> List[JobResponse]:
        async with self.connect() as conn:
            query = "SELECT * FROM jobs WHERE api_key = ? ORDER BY created_at DESC LIMIT ? OFFSET ?"
            async with conn.execute(query, (api_key, limit, offset)) as cur:
                rows = await cur.fetchall()
                results = []
                for row in rows:
                    d = dict(row)
                    key_points = json.loads(d["key_points_json"]) if d.get("key_points_json") else None
                    raw_actions = json.loads(d["action_items_json"]) if d.get("action_items_json") else None
                    action_items = [ActionItem(**a) for a in raw_actions] if raw_actions else None
                    topics = json.loads(d["topics_json"]) if d.get("topics_json") else None

                    results.append(JobResponse(
                        job_id=d["job_id"],
                        title=d["title"],
                        status=d["status"],
                        file_name=d["file_name"],
                        file_size_bytes=d["file_size_bytes"],
                        duration_seconds=d.get("duration_seconds") or 0.0,
                        transcript=d.get("transcript"),
                        summary=d.get("summary"),
                        key_points=key_points,
                        action_items=action_items,
                        sentiment=d.get("sentiment"),
                        topics=topics,
                        error=d.get("error_message"),
                        created_at=str(d.get("created_at")),
                        completed_at=str(d.get("completed_at")) if d.get("completed_at") else None
                    ))
                return results
