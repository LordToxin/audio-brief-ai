# 🎙️ AudioBrief AI — High-Performance Audio Transcription & Executive Summarizer Micro-SaaS API

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Async SQLite](https://img.shields.io/badge/Database-aiosqlite-003B57.svg)](https://github.com/omnilib/aiosqlite)
[![OpenAPI / Swagger](https://img.shields.io/badge/API%20Docs-Swagger%20UI-85EA2D.svg?logo=swagger&logoColor=black)](http://localhost:8000/docs)
[![Tests Passing](https://img.shields.io/badge/tests-5%20passed-brightgreen.svg)]()
[![Docker Ready](https://img.shields.io/badge/docker-ready-2496ED.svg)](https://www.docker.com/)

> **Готовый коммерческий Micro-SaaS бэкенд (Turnkey AI API)** для автоматической транскрибации речи, генерации структурированных Executive Summary, извлечения Action Items (задач с исполнителями) и отправки вебхуков. Заменяет дорогие сервисы вроде Otter.ai, Fireflies и Descript (\$18–\$40/мес на пользователя).

---

## 🎯 Какую боль бизнеса решает продукт?

1. **Часы потерянного времени на прослушивание записей:** продуктовые команды, сейлзы, рекрутеры и топ-менеджеры тратят по 5–10 часов в неделю на повторное прослушивание созвонов.
2. **Потерянные договоренности и задачи:** до 60% поручений на онлайн-встречах забываются. Сервис автоматически вычленяет блок `action_items` с ответственными и приоритетами.
3. **Готовая инфраструктура для B2B:** встроенное управление API-ключами, лимитами запросов и вебхуками позволяет сразу продавать доступ разработчикам или другим компаниям.
4. **Работает «из коробки» (Zero Cold-Start):** поддерживает интеграцию с OpenAI Whisper/GPT, а при отсутствии ключей переключается на встроенный интеллектуальный анализатор — сервер запускается и работает на 100% без дополнительных настроек.

---

## 🏗 Архитектура и пайплайн обработки

```
               +--------------------------------------------+
               |     Клиент (Веб / Мобилка / cURL / CRM)    |
               +---------------------+----------------------+
                                     |
               (POST /api/v1/transcribe with Audio File)
                                     |
                                     v
               +--------------------------------------------+
               |        FastAPI Async Ingestion & Auth      |
               |  - Валидация аудио (mp3, wav, m4a, ogg)    |
               |  - Проверка API-ключа и квоты запросов     |
               |  - Генерация job_id (202 Accepted)         |
               +---------------------+----------------------+
                                     |
                                     v
               +--------------------------------------------+
               |           Background Task Worker           |
               |                                            |
               |  1. Transcription Engine:                  |
               |     OpenAI Whisper API / Local Fallback    |
               |                                            |
               |  2. Intelligence Extractor:                |
               |     - 📝 Executive Summary                 |
               |     - 🎯 Key Discussion Points             |
               |     - ✅ Action Items & Assignees          |
               |     - 📊 Sentiment & Topic Tags            |
               +---------------------+----------------------+
                                     |
                    +----------------+----------------+
                    |                                 |
                    v                                 v
        +-----------------------+         +-----------------------+
        |  Async SQLite DB      |         |  Webhook Callback     |
        |  (Результаты & Статус)|         |  (POST на URL клиента)|
        +-----------------------+         +-----------------------+
```

---

## ⚡ Быстрый старт за 3 минуты

### 1. Клонирование и установка
```bash
git clone https://github.com/Max/audio-brief-ai.git
cd audio-brief-ai

# Создание виртуального окружения
python -m venv venv

# Активация:
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка конфигурации
```bash
cp .env.example .env
```
Файл `.env`:
```ini
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
MASTER_API_KEY=ab_master_sec_9999888877776666

# Опционально: добавьте свой ключ для Whisper/GPT
OPENAI_API_KEY=
```

### 3. Запуск сервера
```bash
uvicorn app.main:app --reload --port 8000
```
Интерактивная документация Swagger доступна по адресу:  
👉 **http://localhost:8000/docs**

### 4. Запуск через Docker
```bash
docker-compose up -d --build
```

---

## 📡 Примеры API-запросов

### 1. Отправка аудио на транскрибацию
```bash
curl -X POST "http://localhost:8000/api/v1/transcribe" \
  -H "X-API-Key: ab_master_sec_9999888877776666" \
  -F "file=@meeting.mp3" \
  -F "title=Sync Meeting" \
  -F "language=ru" \
  -F "webhook_url=https://webhook.site/my-endpoint"
```

**Ответ (202 Accepted):**
```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "title": "Sync Meeting",
  "status": "PENDING",
  "file_name": "meeting.mp3",
  "file_size_bytes": 1048576,
  "created_at": "2026-10-22 18:00:00"
}
```

### 2. Получение результата (`GET /api/v1/jobs/{job_id}`)
```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "title": "Sync Meeting",
  "status": "COMPLETED",
  "duration_seconds": 185.4,
  "transcript": "Коллеги, добрый день! Начинаем наше еженедельное синхронизационное совещание...",
  "summary": "На еженедельном совещании команда подвела итоги подготовки к запуску нового продукта. Бэкенд успешно завершил интеграцию платежного шлюза и обработку вебхуков...",
  "key_points": [
    "Интеграция платежного шлюза и вебхуков завершена и протестирована.",
    "Нагрузочное тестирование показало устойчивость при 2500 RPS.",
    "Необходимо оптимизировать медленные SQL-запросы в таблице транзакций."
  ],
  "action_items": [
    {
      "task": "Оптимизировать SQL-индексы в таблице транзакций",
      "assignee": "Алексей",
      "priority": "High"
    },
    {
      "task": "Утвердить финальные креативы лендинга",
      "assignee": "Марина",
      "priority": "Medium"
    }
  ],
  "sentiment": "Positive",
  "topics": ["Product Launch", "Fintech & Payments", "Performance"]
}
```

### 3. Генерация API-ключа для клиента (`POST /api/v1/auth/keys`)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/keys" \
  -H "X-API-Key: ab_master_sec_9999888877776666" \
  -H "Content-Type: application/json" \
  -d '{"client_name": "Acme SaaS", "tier": "pro", "monthly_limit": 500}'
```

---

## 🧪 Запуск автоматических тестов

```bash
pytest -v
```
Покрывает:
- Проверку жизнеспособности сервиса (`/health`).
- Генерацию API-ключей и валидацию квот.
- Блокировку неавторизованных запросов.
- Загрузку валидного аудио (`.wav`), асинхронное исполнение пайплайна и проверку структуры ответа (`summary`, `action_items`, `key_points`, `sentiment`).
- Отклонение неподдерживаемых файлов.

---

## 💰 Как монетизировать AudioBrief AI

| Модель | Детали реализации | Прогноз дохода |
|---|---|---|
| **API по подписке (Micro-SaaS)** | Тарифы: Starter (\$19/мес за 100 мин), Pro (\$49/мес за 500 мин), Business (\$149/мес за 2000 мин). | **\$500 – \$3,000 / мес** на 20–50 клиентах |
| **Whitelabel бэкенд под ключ** | Развертывание сервиса на сервере клиента (юридические фирмы, медицинские центры, колл-центры). | **\$1,000 – \$3,000** разово за лицензию + поддержка |
| **Интеграция в Telegram-ботов / CRM** | Подключение сервиса как плагина расшифровки голосовых в корпоративный Telegram или Bitrix24/AmoCRM. | **\$300 – \$800** за интеграцию |

---

## 📄 Лицензия
MIT License. Полная свобода коммерческого использования.
