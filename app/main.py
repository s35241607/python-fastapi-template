from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.config import settings
from app.routers import category_router, public_router
from app.auth.dependencies import get_user_id_from_jwt

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

# CORS 中間件設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # 允許的前端來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        # Extract the field name from 'loc'
        field = ".".join([str(loc) for loc in error["loc"] if str(loc) != "body"])
        
        errors.append({
            "field": field,
            "message": error["msg"], # Keep original English message
            "type": error["type"],
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation Error", "errors": errors},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."},
    )

# Mount public routes without global dependencies
app.include_router(public_router.router, dependencies=[])

app.include_router(category_router.router, prefix="/api/v1/categories", tags=["categories"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
