# Trendsetter

Single-tenant (SaaS-ready) social trend intelligence and content planning for TikTok and
Instagram. It polls trending feeds and hashtags through interchangeable provider adapters
(scrapers now, official APIs later), enforces a hard monthly spend cap via a call ledger,
normalizes everything into a TimescaleDB event store, and — in later milestones — detects
bursts, clusters topics, and drafts on-brand content ideas from them.

## Quickstart

```bash
cp .env.example .env          # fill SCRAPECREATORS_API_KEY and FERNET_KEY
docker compose up db -d       # TimescaleDB on localhost:5433
uv sync
uv run alembic upgrade head
uv run trendsetter seed
uv run trendsetter pull-hashtag tiktok fitness
uv run trendsetter costs
uv run uvicorn trendsetter.web.app:app --reload
```

Background worker (periodic trending pulls; skips silently while no API key is set):

```bash
uv run procrastinate --app=trendsetter.worker.tasks.app schema --apply   # once
uv run procrastinate --app=trendsetter.worker.tasks.app worker
```

Or run everything in containers: `docker compose up --build`.

## Architecture

- **Provider registry** (`providers/registry.py`) — resolves `(platform, capability)` to an
  ordered adapter list from `config/providers.yml`; first adapter that succeeds wins,
  `ProviderError`/`QuotaExceededError` fall through to the next.
- **Budget ledger** (`providers/budget.py`) — every external call passes through
  `BudgetedClient` and is recorded in the `provider_calls` hypertable; hard cap raises
  `BudgetExceededError`, soft cap stretches cadences. Caps live in `config/cadence.yml`.
- **Normalize** (`ingest/normalize.py`) — the only DB writer: adapters emit
  `RawPost`/`RawEntity`, normalize upserts entities and appends events.
- **Timescale** — `events`, `event_entities`, `entity_stats_15m`, `embeddings`,
  `provider_calls` are hypertables; SQLite is supported for tests only.
- **Worker** (`worker/tasks.py`) — procrastinate app with periodic tasks wired from
  `config/cadence.yml` via `worker/schedules.py`.

## Status

**M0 (current):** schema + provider abstraction + budget ledger + manual hashtag pulls via
CLI + hourly trending pulls (TikTok, Instagram) in the worker. No detection, no UI beyond a
stub, no LLM features yet. Costs shown by `trendsetter costs` are estimates from
`config/providers.yml` — verify against vendor dashboards.

Roadmap:

- **M1** — scheduled watchlists, 15-minute aggregates, burst scoring against baselines.
- **M2** — embeddings + topic clustering, LLM labeling of clusters.
- **M3** — official APIs (Instagram Graph, TikTok Display) for own-account insights.
- **M4** — content drafting, planning calendar, publishing to R2.

Full build plan: see `docs/plan.md`.
