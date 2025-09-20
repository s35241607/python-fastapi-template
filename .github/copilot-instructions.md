# AI Coding Agent Instructions

## Project Overview

This is a FastAPI-based enterprise ticket management system with complex approval workflows, permissions, and audit trails. The system uses async PostgreSQL with SQLAlchemy 2.0 and follows a router > service > repository architecture pattern.

## Architecture & Data Flow

- **Router Layer**: HTTP request handling, input validation, calls services
- **Service Layer**: Business logic, orchestrates repository operations
- **Repository Layer**: Data access abstraction, interacts with database
- **Database**: PostgreSQL with "ticket" schema, async operations via asyncpg
- **Key Entities**: Tickets, Templates, Approval Processes, Categories, Labels, Notes (unified timeline)

## Critical Developer Workflows

### Environment Setup

```bash
# Install dependencies
uv sync

# Database setup
python init_db.py

# Run development server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
uv run pytest

# Code quality
uv run ruff check . --fix
uv run ruff format .
uv run mypy .
```

### Database Operations

- Use `alembic` for schema migrations (configured for "ticket" schema only)
- Models inherit from `Base` in `app.models.base`
- All tables use audit fields: `created_by`, `updated_by`, `created_at`, `updated_at`
- Soft deletes: `deleted_at`, `deleted_by` fields on all entities
- Foreign keys reference `ticket` schema tables

## Project-Specific Patterns

### Model Conventions

- All models in `ticket` schema (`__table_args__ = {"schema": settings.db_schema}`)
- Enums defined in `app.models.enums` (TicketStatus, TicketPriority, etc.)
- Many-to-many via association tables (e.g., `ticket_categories`, `ticket_labels`)
- JSON fields for custom data (`custom_fields_data`, `event_details`)
- BigInteger for all ID fields

### Repository Pattern

```python
class ExampleRepository(BaseRepository[Model, CreateSchema, UpdateSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = Model
```

- Session injected in constructor
- Generic base provides CRUD operations
- Soft delete support built-in

### Service Layer

- One service per domain (CategoryService, etc.)
- Injects repository via constructor
- Handles business logic and validation
- Returns domain models, not raw data

### Router Layer

- Dependency injection via `Depends(get_service)`
- JWT auth via `get_user_id_from_jwt` (currently no verification in dev)
- Pydantic schemas for request/response validation
- Error handling with HTTPException

### Authentication & Permissions

- JWT tokens (bearer auth)
- User ID extracted from JWT `sub` claim
- Permission system: `internal` (all users) vs `restricted` (explicit permissions)
- Business logic permissions: creators, assignees, approvers get automatic access

### Ticket Lifecycle

- Status enum: draft → waiting_approval → open → in_progress → resolved → closed
- Approval processes with templates and steps
- Unified timeline via `ticket_notes` (user comments + system events)
- Event types: status_change, assignee_change, approval_submitted, etc.

### File Attachments

- Stored in `ticket_attachments` and `ticket_note_attachments`
- File metadata: name, path, size, mime_type
- Soft delete support

## Integration Points

- PostgreSQL async connections via `app.database.get_db()`
- File upload handling (aiofiles)
- Notification rules system (triggers on events)
- Approval workflow engine (multi-step with proxy support)

## Code Quality Standards

- **Linting**: ruff (configured in pyproject.toml)
- **Formatting**: ruff format (128 char line length)
- **Type Checking**: mypy (strict mode, ignore missing imports)
- **Testing**: pytest with asyncio support
- **Imports**: isort via ruff (known-first-party: ["app"])

## Common Patterns to Follow

- Always use async/await for database operations
- Include user_id in create/update operations for audit trails
- Use soft deletes instead of hard deletes
- Add system events to `ticket_notes` for state changes
- Validate permissions before operations on restricted tickets
- Use transactions for multi-table operations
- Follow RESTful API conventions
- Include comprehensive error handling

## Key Files to Reference

- `app/config.py`: Settings and database URL
- `app/models/`: All SQLAlchemy models and enums
- `app/database.py`: Connection setup and session management
- `app/routers/`: API endpoints
- `app/services/`: Business logic
- `app/repositories/`: Data access layer
- `docs/SPEC.md`: Detailed system specifications
- `pyproject.toml`: Dependencies and tool configuration</content>
  <parameter name="filePath">c:\Users\User\Desktop\Template\python-fastapi-template\.github\copilot-instructions.md
