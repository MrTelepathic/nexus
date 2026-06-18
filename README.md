# Nexus

Production-grade AI business platform built entirely on Telegram. Combines an AI assistant, marketplace, social/gamification layer, multi-rail payment system, and no-code automation engine -- all living natively inside Telegram with native-app-quality UI/UX.

## Architecture

```
Client (Telegram Mini App)
        |
   API Gateway (Nginx: rate-limit, TLS, LB)
        |
   +----+----+----+----+
   |         |         |
Bot API   FastAPI   WebSocket
(aiogram)  (REST)   (real-time)
   |         |         |
   +----+----+----+----+
        |
   Message Queue (RabbitMQ + Celery)
        |
   +----+----+
   |         |
AI Core   Services
(LangGraph) (CRM, Payments, Analytics)
        |
   Data Layer
(PostgreSQL + pgvector, Redis, MinIO)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Bot | Python, aiogram 3, webhook/polling |
| Mini App | React, TypeScript, @twa-dev/sdk, TailwindCSS, Framer Motion |
| API | FastAPI, WebSocket, async SQLAlchemy |
| AI | LangGraph, OpenAI API, pgvector, Whisper, TTS |
| Database | PostgreSQL 16 + pgvector, Redis 7, RabbitMQ |
| Storage | MinIO (S3-compatible) |
| Blockchain | TON Connect, Tact smart contracts |
| Infra | Docker, Kubernetes, GitHub Actions CI/CD |
| Observability | Prometheus, Grafana, Sentry |

## Features

### AI Core (Multi-Agent)
- Specialized agents (Sales, Support, Analyst, Moderator) coordinated by LangGraph orchestrator
- Advanced RAG with hybrid search (BM25 + vector + reranking)
- Per-user long-term memory with periodic summarization
- Real-time sentiment analysis for escalation decisions
- Voice pipeline: voice note to Whisper to TTS response
- Vision: product photo analysis via vision model
- Image generation for banners, stickers, custom emoji packs
- Function calling for order placement, invoice generation, reservations
- LLM cost optimization: semantic caching, model routing, local fallback

### Telegram Business Connection
- Auto-reply to customers on behalf of business owner via business_connection_id
- Built-in CRM with per-customer profiles, history, lifetime value, automatic tagging
- ML-based lead scoring
- Scheduled follow-ups and unhappy-customer detection
- Distributed conversation state machine for thousands of concurrent chats

### Telegram Mini App (Bot API 8.0)
- Fullscreen mode with home screen shortcut (installs like a real app)
- Live theme sync with Telegram (light/dark/accent color)
- Haptic feedback on every interaction
- Dynamic MainButton, SecondaryButton, BackButton, SettingsButton
- Closing confirmation, swipe gestures, Framer Motion animations
- Telegram UI Kit for native feel
- Hardware access: biometric auth, QR scanner, accelerometer, gyroscope, location, camera
- Real-time dashboard via WebSocket
- Telegram CloudStorage for data sync

### Native Telegram Features
- Inline Mode for product/content sharing in any chat
- Message Effects on bot messages
- Custom and Premium emoji in text, spoilers, custom link previews
- Reactions API with Paid Reactions (react with Stars)
- Share to Story for viral growth
- Telegram Gifts (Star/NFT gifts between users)
- Emoji Status for VIP customer badges
- Forum Topics, Channel Boosts, Channel Direct Messages
- Native Polls, Quizzes, Channel Giveaways, Star Giveaways
- Voice/Video notes, Live Location for order tracking, Scheduled Messages
- Telegram Passport for KYC, Login Widget for external services

### Triple Payment System
- Telegram Stars (one-time, recurring subscriptions, Star gifts) with full invoice flow and Refund API
- TON blockchain: TON Connect wallet, crypto payments, escrow via smart contract, NFT loyalty badges
- Fiat/card payment rail
- Internal wallet with cashback, points, multi-level referral commissions
- Idempotency and atomicity for all payment methods

### Marketplace
- Product/service listings with dynamic pricing and inventory management
- Verified-purchase reviews and ratings
- P2P escrow for safe user-to-user transactions
- Storefront in Mini App with gallery, filters, smart search

### Social and Gamification
- XP, levels, badges, daily streaks, quests, daily rewards, spin wheel
- Live leaderboard via WebSocket, public shareable profiles
- Friend system and friend challenges
- Multi-level referral tree with dashboard
- Real-time multiplayer mini-games inside Mini App
- Native Telegram HTML5 Games

### No-Code Automation Engine
- Visual if-this-then-that trigger builder
- Connect to Google Sheets, Notion, external services
- Scheduling, conditions, webhooks

### Analytics and BI
- Real-time dashboard (cohort, funnel, retention)
- Automatic AI-generated daily and weekly reports
- Sales forecasting with time-series ML
- A/B testing for messages

## Project Structure

```
nexus/
  backend/
    bot/                  # aiogram 3 bot service
      handlers/           # Command and message handlers
      services/           # Business logic (CRM, payments, AI)
      middleware/          # Logging, tenant resolution, rate limiting
      utils/              # Crypto (initData validation), formatters
    app/                  # FastAPI Mini App backend
      api/v1/             # REST endpoints (auth, dashboard, products, orders)
      api/ws/             # WebSocket for real-time dashboard
      middleware/          # Auth (initData validation), CORS
    ai/                   # AI orchestrator (LangGraph)
      agents/             # Sales, Support, Analyst, Moderator
      tools/              # Function calling tools
      rag/                # Chunking, embedding, retrieval, reranking
      memory/             # Long-term user memory
      llm/                # Model routing, streaming
    payments/             # Stars, TON, fiat abstraction
    db/                   # SQLAlchemy models and migrations
      models/             # 13 domain models with RLS
      migrations/         # Alembic versioned migrations
    realtime/             # WebSocket manager, Celery app
    tasks/                # Async tasks (AI, payments, notifications)
    blockchain/           # TON Connect, Tact smart contracts
    tests/                # pytest test suite
  miniapp/                # React + TypeScript Mini App
    src/
      providers/          # TWA, Theme, Auth, WebSocket providers
      hooks/              # useMainButton, useBackButton, useHaptic, useBiometric
      pages/              # Dashboard, Products, Wallet, Profile, Leaderboard
      components/         # UI primitives, layout, dashboard, gamification
      stores/             # Zustand state management
      lib/                # API client, utilities
  contracts/              # TON smart contracts (Tact)
  infra/
    docker/               # Docker Compose, Nginx config
    k8s/                  # Kubernetes manifests, HPA, network policies
  .github/workflows/      # CI/CD pipelines
```

## Database

PostgreSQL with pgvector for vector search and Row-Level Security for multi-tenancy.

Key tables: tenants, users, conversations, messages, products, orders, payments, wallets, user_gamification, badges, referrals, knowledge_base, llm_cache.

Every table with tenant_id has an RLS policy. The application sets the tenant context on every database connection via `set_current_tenant()`.

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 16 with pgvector extension
- Redis 7
- Node.js 20+
- A Telegram Bot Token from @BotFather

### 1. Clone and configure

```bash
git clone https://github.com/your-org/nexus.git
cd nexus
cp .env.example .env
```

Edit `.env` and set at minimum:
- `BOT_TOKEN` -- your Telegram bot token
- `DATABASE_URL` -- PostgreSQL connection string
- `REDIS_URL` -- Redis connection string

### 2. Start infrastructure

```bash
docker compose -f infra/docker/docker-compose.yml up -d postgres redis
```

Or run PostgreSQL and Redis natively.

### 3. Create database schema

```bash
docker exec -i nexus-postgres psql -U nexus -d nexus < schema.sql
```

The schema SQL includes all tables, indexes, RLS policies, and triggers.

### 4. Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 5. Run the bot

```bash
cd backend
PYTHONPATH=. python -m bot.main
```

In development without a webhook URL, the bot runs in polling mode.

### 6. Run the API server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 7. Run the Mini App

```bash
cd miniapp
npm install
npm run dev
```

The Mini App dev server starts on port 3000.

## Running Tests

```bash
cd backend
pytest -x -v
```

## Linting and Type Checking

```bash
cd backend
ruff check .
ruff format .
mypy .
```

## Deployment

### Docker

```bash
docker compose -f infra/docker/docker-compose.yml up -d
```

### Kubernetes

```bash
kubectl apply -f infra/k8s/base/namespace.yml
kubectl apply -f infra/k8s/base/secrets.yml
kubectl apply -f infra/k8s/base/configmap.yml
kubectl apply -f infra/k8s/services/
kubectl apply -f infra/k8s/ingress.yml
kubectl apply -f infra/k8s/hpa.yml
```

### CI/CD

GitHub Actions workflows in `.github/workflows/`:
- `ci.yml` -- lint, typecheck, test on push/PR
- `cd.yml` -- build, push container, deploy on merge to main
- `security.yml` -- SAST and dependency scanning

## Security

Sensitive areas and their mitigations:

- **Mini App initData validation**: HMAC-SHA-256 with bot token as secret key, timestamp freshness check (max 24h), nonce store in Redis for replay prevention.
- **Bot token storage**: Encrypted at rest, never logged, environment-only in production.
- **Payment idempotency**: UNIQUE constraint on idempotency_key in payments and orders tables. Every payment processed exactly once via ON CONFLICT.
- **Row-Level Security**: Every database connection sets tenant context. RLS policies enforce data isolation at the database level.
- **Rate limiting**: Redis sliding window per user, per callback type. API gateway rate limiting via Nginx.
- **Secrets management**: Environment variables only, never committed. GitHub Actions secrets for CI/CD.
- **LLM prompt injection**: Input sanitization, tool-call allowlisting, human-in-the-loop for financial actions.

## Configuration

All configuration is loaded from environment variables via pydantic-settings. See `.env.example` for the full list.

Key configuration groups:
- Application (env, debug, secret key)
- Telegram (bot token, webhook URL, Mini App URL)
- Database (PostgreSQL connection pool)
- Redis (cache TTL, session store)
- AI/LLM (OpenAI keys, model selection, budget model)
- Blockchain (TON network, escrow address)
- Payment (Stars provider token, fiat API keys)
- Observability (Sentry DSN, trace sampling)

## License

MIT
