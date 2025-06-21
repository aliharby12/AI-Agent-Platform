from fastapi import FastAPI
from app.api.routers.agent_routes import router as agent_router
from app.api.routers.session_routes import router as session_router
from app.utils.database import init_db
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="AI Agent Platform", description="Backend for AI Agent Platform with text and voice interaction")

# Mount static directory for serving audio files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(agent_router)
app.include_router(session_router)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "AI Agent Platform API"}