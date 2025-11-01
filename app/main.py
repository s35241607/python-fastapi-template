from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from app.config import settings
from app.handlers.error_handlers import register_exception_handlers
from app.routers import attachment_router, category_router, devtools_router, label_router, public_router, ticket_router

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     # Shutdown
#     await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
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


# CORS 中間件設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # 允許的前端來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount public routes without global dependencies
app.include_router(public_router, dependencies=[])

# Devtools router to inspect JWT payloads (dev behavior: no signature verification)
app.include_router(devtools_router, prefix="/api/v1/test", tags=["test"])

app.include_router(category_router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(label_router, prefix="/api/v1/labels", tags=["labels"])
app.include_router(ticket_router, prefix="/api/v1/tickets", tags=["tickets"])
app.include_router(attachment_router, prefix="/api/v1/attachments", tags=["attachments"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
