import uuid

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from app.config import settings
from app.core.structlog_config import get_logger, setup_logging
from app.handlers.error_handlers import register_exception_handlers
from app.middleware.access_log_middleware import AccessLogMiddleware
from app.routers import attachment_router, category_router, devtools_router, label_router, public_router, ticket_router

# Initialize logging system BEFORE anything else
setup_logging()

log = get_logger(__name__)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     # Shutdown
#     await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    security=[{"BearerAuth": []}],  # Add global security for Swagger UI
    openapi_extra={
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        },
    },
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Register exception handlers BEFORE adding middleware
register_exception_handlers(app)

# ============================================================================
# Middleware Stack (Order matters - LAST added runs FIRST in Starlette!)
# ============================================================================

# 3. CORS Middleware (runs last - innermost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # 允許的前端來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Access Log Middleware (runs second)
app.add_middleware(AccessLogMiddleware)

# 1. Correlation ID Middleware (runs first - outermost, sets request_id for all following middleware)
#    Reads X-Request-ID from nginx/kong or generates a new one
app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Request-ID",  # Match nginx/kong header
    update_request_header=True,  # Ensure request.headers also has it
    generator=lambda: uuid.uuid4().hex,  # Generate if not present
    transformer=lambda x: x,  # No transformation needed
    validator=lambda x: len(x) > 0 and len(x) <= 256,  # Accept any non-empty string up to 256 chars
)


# Mount public routes without global dependencies
app.include_router(public_router, dependencies=[])

# Devtools router to inspect JWT payloads (dev behavior: no signature verification)
app.include_router(devtools_router, prefix="/api/v1/test", tags=["test"])

app.include_router(category_router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(label_router, prefix="/api/v1/labels", tags=["labels"])
app.include_router(ticket_router, prefix="/api/v1/tickets", tags=["tickets"])
app.include_router(attachment_router, prefix="/api/v1/attachments", tags=["attachments"])

log.info(
    "Application startup complete",
    app_name=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    environment=settings.ENVIRONMENT,
)


if __name__ == "__main__":
    import uvicorn

    # Disable uvicorn's default logging config to use our structlog setup
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
