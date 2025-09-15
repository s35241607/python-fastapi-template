from fastapi import FastAPI
from app.routers import items
from app.database import engine
from app.models.base import Base
import asyncio

app = FastAPI(title="FastAPI Template", version="1.0.0")

app.include_router(items.router, prefix="/api/v1", tags=["tickets"])

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Ticket System"}

@app.on_event("startup")
async def startup_event():
    # 創建資料庫表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
