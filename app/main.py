from fastapi import FastAPI
from app.api.routes import router
from app.utils.database import init_db

app = FastAPI(title="AI Agent Platform", description="Backend for AI Agent Platform with text and voice interaction")

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "AI Agent Platform API"}