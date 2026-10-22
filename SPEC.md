# SPEC: AudioBrief AI — High-Performance Audio Transcription & Executive Summarizer Micro-SaaS API

## 1. Executive Summary
**AudioBrief AI** is a production-grade FastAPI micro-service and turn-key Micro-SaaS backend for audio transcription, executive summary synthesis, meeting action-item extraction, and asynchronous webhook delivery. It provides an immediate alternative to expensive commercial meeting intelligence solutions (Otter.ai, Fireflies, Descript) with self-hosted control and zero cold-start dependencies.

## 2. Technical Stack & Architecture
- **Framework**: Python 3.11+, FastAPI (Async ASGI), Uvicorn.
- **Database**: Async SQLite (`aiosqlite`) with WAL mode for high concurrency.
- **AI / Speech-to-Text Engine**: Dual-mode transcription:
  - OpenAI Whisper API (production cloud mode)
  - Intelligent local heuristic extractor fallback (zero cold-start, 100% offline testable)
- **Security & Multi-Tenancy**:
  - API Key authentication via `X-API-Key` headers.
  - Per-key quota throttling and monthly usage tracking.
  - Role-based separation (Master Admin key vs Client API keys).
- **Background Tasks & Webhooks**:
  - Asynchronous background worker queue.
  - HTTP Webhook callbacks with JSON payload and retry logic.
- **Containerization**: Multi-stage Dockerfile and `docker-compose.yml`.

## 3. API Endpoints
- `GET /health`: Health status and system uptime.
- `POST /api/v1/auth/keys`: Multi-tenant client API key generation with tier and monthly quota assignment.
- `POST /api/v1/transcribe`: Asynchronous file ingestion (`mp3`, `wav`, `m4a`, `ogg`) returning `202 Accepted` with `job_id`.
- `GET /api/v1/transcribe/{job_id}`: Job status polling, transcription text, action items, sentiment analysis, and topic tags.

## 4. Monetization Strategy
- **Micro-SaaS API Subscription**: Starter ($19/mo, 100 min), Pro ($49/mo, 500 min), Business ($149/mo, 2,000 min).
- **White-Label Enterprise License**: Turnkey deployment for legal, healthcare, or financial firms ($1,000 - $3,000 one-time + annual maintenance).
- **CRM & Telegram Bot Integrations**: Voice memo transcription plugin for Telegram corporate groups and CRM voice call logging ($300 - $800 / integration).
