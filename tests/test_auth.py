import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User

@pytest.mark.asyncio
async def test_register_user(client: TestClient, db_session: AsyncSession):
    response = client.post("/auth/register", json={"username": "testuser", "password": "securepassword"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data
    assert "created_at" in data

    # Verify user in database using SQLAlchemy ORM
    result = await db_session.execute(select(User).where(User.username == "testuser"))
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.username == "testuser"

@pytest.mark.asyncio
async def test_register_duplicate_user(client: TestClient):
    client.post("/auth/register", json={"username": "testuser", "password": "securepassword"})
    response = client.post("/auth/register", json={"username": "testuser", "password": "otherpassword"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already exists"}

@pytest.mark.asyncio
async def test_login_user(client: TestClient):
    client.post("/auth/register", json={"username": "testuser", "password": "securepassword"})
    response = client.post("/auth/login", json={"username": "testuser", "password": "securepassword"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: TestClient):
    response = client.post("/auth/login", json={"username": "testuser", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}

@pytest.mark.asyncio
async def test_refresh_token(client: TestClient, access_token: str):
    client.post("/auth/register", json={"username": "testuser", "password": "securepassword"})
    login_response = client.post("/auth/login", json={"username": "testuser", "password": "securepassword"})
    refresh_token = login_response.json()["refresh_token"]
    response = client.post("/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"