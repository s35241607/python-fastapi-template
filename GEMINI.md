# FastAPI Ticket System Context

## Project Overview
This is an enterprise-grade ticket management system backend built with **Python 3.12+** and **FastAPI**. It follows a strict layered architecture (**Router → Service → Repository**) and utilizes **SQLAlchemy 2.0** for asynchronous database interactions.

## Tech Stack
- **Language:** Python 3.12+
- **Web Framework:** FastAPI
- **Database:** PostgreSQL (Production), SQLite (Dev default)
- **ORM:** SQLAlchemy 2.0 (Async)
- **Migrations:** Alembic
- **Validation:** Pydantic V2
- **Package Manager:** `uv`
- **Testing:** Pytest
- **Linting/Formatting:** Ruff
- **Type Checking:** MyPy

## Architecture & Patterns
The project adheres to a strict layered architecture:
1.  **Routers (`app/routers/`)**: Handle HTTP requests, input validation (via Pydantic), and response formatting. **NO business logic.** **NO try-except blocks** (rely on global exception handlers).
2.  **Services (`app/services/`)**: Contain all business logic, validation rules, and transaction management. Orchestrate calls to repositories.
3.  **Repositories (`app/repositories/`)**: Handle direct database interactions (CRUD). Inherit from `BaseRepository` for common operations.
4.  **Models (`app/models/`)**: SQLAlchemy ORM models. All tables reside in the `ticket` schema.
5.  **Schemas (`app/schemas/`)**: Pydantic models for request/response validation.

### Key Conventions
- **Async/Await**: All I/O operations (DB, API calls) must be asynchronous.
- **Database Schema**: All tables belong to the `ticket` schema (`__table_args__ = {"schema": settings.db_schema}`).
- **Audit Fields**: All models track `created_by`, `created_at`, `updated_by`, `updated_at`, `deleted_by`, `deleted_at`.
- **Soft Deletes**: Entities use `is_deleted` flag. Repositories handle this automatically.
- **Error Handling**:
    - **Routers**: Do NOT use `try-except`. Let exceptions bubble up.
    - **Services**: Raise `HTTPException` for business rule violations.
    - **Global**: `app/handlers/error_handlers.py` catches and formats errors.
- **Request Validation**: **ALWAYS** use Pydantic models for request bodies/forms. **NEVER** use individual `Form(...)` parameters in router functions.

## Database & Models
- **`ticket` Schema**: Contains all application tables.
- **Core Tables**: `tickets`, `categories`, `labels`, `ticket_templates`.
- **Approval System**: `approval_templates`, `approval_process_steps`, etc., for flexible workflows.
- **Timeline**: `ticket_notes` stores all comments and system events (status changes, etc.).
- **Permissions**: `ticket_view_permissions` for granular access control.

## Development Workflow

### 1. Setup & Install
```bash
# Install dependencies
uv sync
```

### 2. Database Initialization
```bash
# Initialize DB (creates tables in SQLite or Postgres)
uv run python init_db.py
```

### 3. Run Development Server
```bash
# Starts API at http://localhost:8000
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Testing & Quality
```bash
# Run tests
uv run pytest

# Lint & Fix
uv run ruff check . --fix

# Format
uv run ruff format .

# Type Check
uv run mypy .
```

## Configuration
- **Environment Variables**: Managed via `.env` file (see `.env.example`).
- **Database URL**: Always use PostgreSQL. Set `DATABASE_URL` in your `.env` file to a PostgreSQL connection string. Example: `postgresql+asyncpg://user:pass@host/dbname`
- **Settings**: Loaded via `app.config.settings`.

## Folder Structure
- `app/`: Main application source code.
    - `auth/`: Authentication logic.
    - `handlers/`: Global exception handlers.
    - `models/`: SQLAlchemy models.
    - `repositories/`: Database access layer.
    - `routers/`: API endpoints.
    - `schemas/`: Pydantic models.
    - `services/`: Business logic.
- `alembic/`: Database migrations.
- `docs/`: Documentation and specifications.
- `tests/`: Unit and integration tests.

## Implementation Guidelines
- **New Features**: Start by defining Pydantic schemas, then the Repository, then the Service, and finally the Router.
- **Transactions**: Transactions are request-scoped and managed automatically by `get_db`. Repositories perform `flush()`, and the global dependency handles `commit()` on success or `rollback()` on error. Do NOT manually commit in services unless specifically required for isolated logic.
- **Context**: Always pass `user_id` to repository methods for audit trail population.
