from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers.agent_routes import router as agent_router
from app.api.routers.session_routes import router as session_router
from app.api.routers.auth_routes import router as auth_router
from app.utils.database import init_db
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()  # Startup logic
    yield

app = FastAPI(
    title="AI Agent Platform", 
    description="Backend for AI Agent Platform with text and voice interaction",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Operations for user authentication and authorization"
        },
        {
            "name": "Agents", 
            "description": "Operations for managing AI agents"
        },
        {
            "name": "Sessions",
            "description": "Operations for chat sessions"
        }
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for serving audio files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(agent_router)
app.include_router(session_router)
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "AI Agent Platform API"}