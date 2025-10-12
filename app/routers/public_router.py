from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Welcome to FastAPI Ticket System"}


@router.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "service": "FastAPI Ticket System"}
