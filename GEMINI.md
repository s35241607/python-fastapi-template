# Gemini Code Assistant Context

This brief guides assistants to be productive in this repo immediately.

## Overview

- Backend: FastAPI + SQLAlchemy 2.0 (async)
- DB: Default SQLite (aiosqlite) via `app.database`; switch to PostgreSQL by setting `DATABASE_URL` (asyncpg)
- Tooling: `uv` (deps/runtime), `ruff` (lint/format), `mypy` (types), `pytest`
- Domain: Enterprise ticketing with `ticket` schema (Alembic migrations restricted to this schema)

## Architecture

Router → Service → Repository pattern:
- Routers (FastAPI) handle validation and delegate to services
- Services hold business logic and orchestrate repositories
- Repositories receive `AsyncSession` in ctor and provide CRUD; see `repositories/base_repository.py`

Key models: see `app/models` (enums, ticket, category, labels, approvals). All tables have audit fields and soft-delete columns.

## Runbook

```pwsh
# Install deps
uv sync

# Create tables (uses app.database engine; SQLite by default)
uv run python init_db.py

# Dev server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Tests and quality
uv run pytest
uv run ruff check . --fix
uv run ruff format .
uv run mypy .
```

Alembic is configured (see `alembic/env.py`) to include only objects in `settings.db_schema` (default `ticket`). Update `alembic.ini` `sqlalchemy.url` to a reachable PostgreSQL when running migrations.

## Auth and Permissions

- Bearer JWT required by protected routers; in dev, `get_user_id_from_jwt` decodes without signature verification and reads `sub` as user id.
- Visibility and permission rules are defined in `docs/SPEC.md`; data structures exist in models (e.g., `ticket_view_permissions`).

## Implemented Endpoints (now)

- Public: `GET /` → welcome payload
- Categories: `/api/v1/categories` CRUD (requires Bearer)

Use `category_router.py` + `category_service.py` + `category_repository.py` as the pattern to add Tickets/Approvals/Labels routes.

## Conventions & Gotchas

- All models are in `ticket` schema; ensure `__table_args__ = {"schema": settings.db_schema}` when adding tables (or use existing patterns)
- Use JSON fields for flexible data (`custom_fields_data`, `event_details`)
- Enums live in `app/models/enums.py` and are schema-qualified in Alembic
- Always pass `user_id` on create/update to populate audit fields when applicable
- Prefer soft-delete; repositories include helpers
- For multi-table updates (e.g., approval flow), wrap in a transaction (`AsyncSession`)

## Troubleshooting

- Uvicorn exits (code 1): verify `.env` `DATABASE_URL` or start with default SQLite and run `uv run python init_db.py`
- Alembic missing objects: ensure you’re targeting the `ticket` schema and that models include schema in `__table_args__`
