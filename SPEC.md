# Product Specification: AudioBrief AI (Speech-to-Summary Micro-SaaS API)

## 1. Executive Summary & Value Proposition
**AudioBrief AI** is an asynchronous audio transcription and executive briefing engine built on FastAPI, aiosqlite, and OpenAI Whisper/GPT. It ingests audio recordings (MP3, WAV, M4A, OGG, WebM), generates structured executive summaries, extracts actionable tasks with priority assignments, and dispatches real-time webhooks.

## 2. Target Market
- **B2B SaaS Founders & Product Teams**: Summarizing client discovery calls and sprint planning sessions.
- **Consultancies & Recruitment Agencies**: Generating structured interview debriefs and client proposals.
- **Developers & Integrators**: White-label transcription and intelligence API with ready-made API key management.

## 3. Architecture & API Endpoints
- `POST /api/v1/auth/keys`: Provision new API keys with configurable rate limits.
- `GET /api/v1/auth/keys`: List active API keys and usage statistics.
- `POST /api/v1/transcribe`: Ingest audio file (multiform), enqueue background transcription and summary synthesis.
- `GET /api/v1/jobs/{job_id}`: Poll status and retrieve structured briefing results.
- `GET /health`: System healthcheck and status monitoring.

## 4. Technology Stack
- **Framework**: FastAPI (Python 3.11+ / 3.13)
- **Database**: Async SQLite (`aiosqlite`) with WAL mode
- **Testing**: `pytest`, `pytest-asyncio`, `httpx`
- **Containerization**: Minimal Alpine/Slim Docker image and Docker Compose

## 5. Monetization Strategy
- **Usage-Based API Billing**: $0.05/minute of processed audio.
- **Monthly Subscription ($19 - $49/mo)**: Included quotas with priority worker queues.
- **Self-Hosted Enterprise License ($499)**: Turnkey Docker Compose package for privacy-conscious enterprise deployments.
