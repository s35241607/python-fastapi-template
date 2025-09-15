from fastapi import FastAPI
from app.routers import items

app = FastAPI(title="FastAPI Template", version="1.0.0")

app.include_router(items.router, prefix="/api/v1", tags=["items"])

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Template"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
