import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.utils.database import get_db
from backend.models.base import Base
from backend.models.user import User
from backend.api.dependencies import get_openai_client, hash_password
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from jose import jwt
import os
from dotenv import load_dotenv

# Try to load .env file, but don't fail if it doesn't exist
try:
    load_dotenv()
except OSError:
    pass  # Ignore the error if .env file is not found

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def client(db_session):
    def override_get_db():
        yield db_session

    def override_get_openai_client():
        client = MagicMock()
        client.chat.completions.create = AsyncMock(return_value=MagicMock(choices=[MagicMock(message=MagicMock(content="Mocked response"))]))
        client.audio.transcriptions.create = AsyncMock(return_value=MagicMock(text="Mocked transcription"))
        client.audio.speech.create = AsyncMock(return_value=MagicMock(content=b"mocked audio data"))
        yield client

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_openai_client] = override_get_openai_client
    
    # Create TestClient without context manager to avoid compatibility issues
    test_client = TestClient(app)
    yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def user_credentials():
    return {"username": "testuser", "password": "securepassword"}

@pytest_asyncio.fixture
async def access_token(user_credentials, db_session):
    # Create a user in the database first
    test_user = User(username=user_credentials["username"], password_hash=hash_password(user_credentials["password"]))
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)
    
    # Generate token for the created user
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode = {"sub": user_credentials["username"], "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)