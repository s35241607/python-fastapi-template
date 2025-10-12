# FastAPI Ticket System - AI Coding Assistant Instructions

## Project Overview
Enterprise-grade ticket management system built with FastAPI + SQLAlchemy 2.0 async ORM. Features approval workflows, permissions, unified timeline, and comprehensive audit trails. All database objects reside in the `ticket` schema.

## Architecture Pattern
**Router → Service → Repository** layered architecture:
- **Routers** (`app/routers/`): Handle HTTP requests, validation, and response formatting
- **Services** (`app/services/`): Contain business logic and orchestrate repository calls
- **Repositories** (`app/repositories/`): Provide data access with generic CRUD operations

Example pattern from `category_router.py` → `category_service.py` → `category_repository.py`

## Database & Models
- **Default**: SQLite (`sqlite+aiosqlite:///./test.db`) for development
- **Production**: PostgreSQL via `DATABASE_URL` env var
- **Schema**: All tables in `ticket` schema (`__table_args__ = {"schema": settings.db_schema}`)
- **Audit Fields**: All models include `created_by/at`, `updated_by/at`, `deleted_by/at`
- **Soft Delete**: `is_deleted` boolean field on all entities
- **Enums**: Centralized in `app/models/enums.py`

### Key Database Tables (from `docs/ticket_system_schema.sql`)

#### Core Entities
- **`tickets`**: Main ticket table with status, priority, visibility, custom fields
- **`categories`** & **`labels`**: Reusable classification system
- **`ticket_templates`**: Reusable ticket blueprints with custom fields schema

#### Relationships & Associations
- **`ticket_categories`** & **`ticket_labels`**: Many-to-many ticket associations
- **`ticket_template_categories`** & **`ticket_template_labels`**: Template associations

#### Approval System
- **`approval_templates`**: Reusable approval workflows
- **`approval_template_steps`**: Steps within templates (all/any approval types)
- **`approval_template_step_approvers`**: Who approves each step (users/roles)
- **`approval_processes`**: Active approval instances for tickets
- **`approval_process_steps`**: Current step status in active processes
- **`approval_process_step_approvers`**: Individual approver status with proxy support

#### Unified Timeline
- **`ticket_notes`**: All historical events (user comments + system events)
  - `system=true`: Automated events with `event_type` and `event_details` JSON
  - `system=false`: User comments in `note` field

#### Permissions & Security
- **`ticket_view_permissions`**: Granular access control for restricted tickets
- **`attachments`**: Unified file storage for tickets, notes, templates

#### Notifications
- **`notification_rules`**: Event-driven notification triggers
- **`notification_rule_users`** & **`notification_rule_roles`**: Notification recipients

## Authentication & Authorization
- **JWT Bearer tokens** required for protected endpoints
- **Dev Mode**: `get_user_id_from_jwt()` reads `sub` claim without signature verification
- **Permissions**: `internal` (visible to all) vs `restricted` (role-based access via `ticket_view_permissions`)
- **Business Logic Permissions**: Ticket creators, approvers, and assignees get automatic access

## Key Workflows

### Development Setup
```bash
# Install dependencies
uv sync

# Initialize database (creates tables)
uv run python init_db.py

# Start dev server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
uv run pytest

# Code quality
uv run ruff check . --fix
uv run ruff format .
uv run mypy .
```

### Database Migrations
- **Alembic** configured to only migrate `ticket` schema objects
- Update `alembic.ini` `sqlalchemy.url` for PostgreSQL
- Use `alembic/env.py` `include_object()` filter for schema isolation

## Coding Conventions

### Code Style
- **Line length**: 128 characters
- **Quotes**: Double quotes (`"`)
- **Imports**: `known-first-party = ["app"]` (app imports after third-party)
- **Formatting**: Ruff handles both linting and formatting

### Error Handling (STRICT REQUIREMENT)
- **NEVER use try-catch blocks in Router layer**: Global exception handlers exist for consistent error responses
- **Business logic validation belongs in Service layer**: Services should raise HTTPException for business rule violations
- **Router layer focuses on HTTP concerns only**: Parameter extraction, response formatting, basic HTTP status codes
- **Global error handlers provide consistent responses**: All errors bubble up through service → repository layers

### Request Validation (STRICT REQUIREMENT)
- **ALWAYS use Pydantic models for request validation**: Never use individual Form/File parameters in router functions
- **Define request models in schemas**: Create specific request models for each endpoint (e.g., `AttachmentUploadRequest`)
- **Use Depends() for complex requests**: Form data should be encapsulated in Pydantic models, not individual parameters
- **Type safety through schemas**: All request data must be validated through Pydantic BaseModel classes

### Repository Pattern
```python
# Constructor injection
def __init__(self, db: AsyncSession):
    self.db = db

# Always pass user_id for audit fields
await repo.create(obj_in, user_id=current_user_id)
await repo.update(obj_id, obj_in, user_id=current_user_id)
```
```python
# Constructor injection
def __init__(self, db: AsyncSession):
    self.db = db

# Always pass user_id for audit fields
await repo.create(obj_in, user_id=current_user_id)
await repo.update(obj_id, obj_in, user_id=current_user_id)
```

### Transaction Management
```python
# Wrap multi-table operations in transactions
async with AsyncSession(engine) as session:
    async with session.begin():
        # ... multiple repository calls ...
```

### Model Definitions
```python
class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = {"schema": settings.db_schema}

    # Always include audit fields
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    # ... other fields
```

## Business Logic Patterns

### Ticket Lifecycle (from `docs/SPEC.md`)
Status transitions with business rules:
- `draft` → `waiting_approval` → `open` → `in_progress` → `resolved` → `closed`
- `draft` → `cancelled` (creator only)
- `waiting_approval` → `rejected` (any approver)
- State changes trigger approval processes and notifications
- All state changes logged in `ticket_notes` as system events

### Approval Engine
- Templates define reusable approval flows (`approval_templates` + `approval_template_steps`)
- Instances track active approvals (`approval_processes` + `approval_process_steps`)
- Support for proxy approvers (delegated approval rights)
- Two approval types: `all` (unanimous) and `any` (any single approval)

### Unified Timeline
- `ticket_notes` table stores all historical events
- `system=True` for automated events, `system=False` for user comments
- JSON `event_details` for structured event data
- Event types: `status_change`, `assignee_change`, `label_add`, etc.

### Permission System
- **Static Permissions**: `internal` tickets visible to all, `restricted` require explicit permissions
- **Business Logic Permissions**: Automatic access for creators, approvers, assignees
- **Permission Requests**: Users can request access to restricted tickets
- All access logged in `ticket_notes` as system events

## Common Gotchas

### Database Connections
- Always use `AsyncSession` from `app.database.get_db()` dependency
- Never create sessions manually in business logic
- Default SQLite works for development; set `DATABASE_URL` for PostgreSQL

### Schema Qualification
- All new models must include `__table_args__ = {"schema": settings.db_schema}`
- Enums must be schema-qualified in Alembic migrations
- Foreign keys reference schema-qualified tables

### User Context
- Always extract `user_id` from JWT in protected routes
- Pass `user_id` to repository methods for audit trail population
- Handle proxy approvers in approval workflows

### Error Handling
- Use FastAPI's exception handlers for consistent error responses
- Log business logic errors with appropriate context
- Rollback transactions on failures

## Testing Strategy
- **Unit tests** in `tests/unit/` for models, repositories, services
- **Integration tests** for routers and end-to-end flows
- Use `pytest-asyncio` for async test functions
- Mock external dependencies (notifications, external auth systems)

## File Structure Reference
```
app/
├── main.py              # FastAPI app, CORS, route mounting
├── config.py            # Pydantic settings (DATABASE_URL, db_schema=ticket)
├── database.py          # Async engine/session factory, get_db() DI
├── models/              # SQLAlchemy models (all schema-qualified)
├── repositories/        # Generic CRUD with soft delete support
├── services/            # Business logic orchestration
├── routers/             # HTTP endpoints and validation
└── schemas/             # Pydantic request/response models
```

## Extension Patterns
When adding new features:
1. Follow Router → Service → Repository pattern
2. **STRICT**: Add business logic validation to Service layer, NEVER use try-catch in routers
3. **STRICT**: Define Pydantic request models for ALL router endpoints, never use individual Form parameters
4. Add audit fields to new models
5. Include schema qualification
6. Update `ticket_notes` for system events
7. Add permission checks for restricted operations
8. Wrap multi-table operations in transactions
9. Add comprehensive tests

Reference `category_*` files as the canonical implementation example.

## Development Roadmap (from `docs/plans/ticket_development_plan.md`)
**Incremental development strategy** - start simple, build complexity gradually:

### Phase 1: Basic Ticket CRUD
- Implement Ticket schemas, repository, service, router
- Basic create/read/update operations
- Simple permission checks (creator-only access)
- Reference `category_*` files for implementation patterns

### Phase 2: Status Management
- Add status transition logic and validation
- Implement basic timeline (system events in `ticket_notes`)
- Status change API endpoints

### Phase 3: Advanced Features
- Category/Label associations
- Full permission system (internal vs restricted visibility)
- Approval workflows using existing `approval_*` tables
- Notification system integration

### Implementation Tips
- **Copy existing patterns**: Use Category/Label implementations as templates
- **Test incrementally**: Add basic functionality first, then enhance
- **Database-first approach**: Schema already defined, implement models accordingly
- **Start with simple permissions**: Creator-only access, then expand to full permission system
