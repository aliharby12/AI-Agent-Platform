import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.models.user import User
from jose import jwt
import os
from datetime import datetime, timezone, timedelta

@pytest.mark.asyncio
async def test_register_user_success(client: TestClient, db_session: AsyncSession):
    response = client.post("/auth/register", json={"username": "testuser", "password": "securepassword"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data  # Password should not be returned

    # Verify user in database
    result = await db_session.execute(select(User).where(User.username == "testuser"))
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.username == "testuser"
    assert user.password_hash is not None
    assert user.password_hash != "securepassword"  # Should be hashed

@pytest.mark.asyncio
async def test_register_user_short_password(client: TestClient):
    """Test registration with very short password"""
    response = client.post("/auth/register", json={"username": "testuser", "password": "123"})
    # Note: Your current implementation doesn't validate password length
    # This test documents current behavior - you might want to add validation
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_register_duplicate_user_exact_match(client: TestClient):
    client.post("/auth/register", json={"username": "testuser", "password": "securepassword"})
    response = client.post("/auth/register", json={"username": "testuser", "password": "otherpassword"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already exists"}

@pytest.mark.asyncio
async def test_register_user_case_sensitivity(client: TestClient):
    """Test if usernames are case-sensitive"""
    client.post("/auth/register", json={"username": "testuser", "password": "securepassword"})
    response = client.post("/auth/register", json={"username": "TestUser", "password": "otherpassword"})
    # This documents current behavior - case sensitive usernames
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_register_user_special_characters(client: TestClient):
    """Test registration with special characters in username"""
    special_username = "test_user@domain.com"
    response = client.post("/auth/register", json={"username": special_username, "password": "securepassword"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == special_username

@pytest.mark.asyncio
async def test_login_user_success(client: TestClient):
    client.post("/auth/register", json={"username": "testuser", "password": "securepassword"})
    response = client.post("/auth/login", json={"username": "testuser", "password": "securepassword"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    
    # Verify tokens are valid JWTs
    secret_key = os.getenv("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    
    access_payload = jwt.decode(data["access_token"], secret_key, algorithms=[algorithm])
    assert access_payload["sub"] == "testuser"
    assert "exp" in access_payload
    
    refresh_payload = jwt.decode(data["refresh_token"], secret_key, algorithms=[algorithm])
    assert refresh_payload["sub"] == "testuser"
    assert "exp" in refresh_payload

@pytest.mark.asyncio
async def test_login_user_wrong_password(client: TestClient):
    client.post("/auth/register", json={"username": "testuser", "password": "securepassword"})
    response = client.post("/auth/login", json={"username": "testuser", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}

@pytest.mark.asyncio
async def test_login_user_nonexistent(client: TestClient):
    response = client.post("/auth/login", json={"username": "nonexistent", "password": "securepassword"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}

@pytest.mark.asyncio
async def test_login_user_case_sensitivity(client: TestClient):
    """Test login with different case username"""
    client.post("/auth/register", json={"username": "testuser", "password": "securepassword"})
    response = client.post("/auth/login", json={"username": "TestUser", "password": "securepassword"})
    assert response.status_code == 401  # Case sensitive

@pytest.mark.asyncio
async def test_login_missing_username(client: TestClient):
    response = client.post("/auth/login", json={"password": "securepassword"})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_refresh_token_invalid_token(client: TestClient):
    response = client.post("/auth/refresh", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_refresh_token_no_token(client: TestClient):
    response = client.post("/auth/refresh")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_refresh_token_expired(client: TestClient):
    """Test refresh with expired token"""
    # Create an expired token
    secret_key = os.getenv("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    
    expired_token_data = {
        "sub": "testuser",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1)  # Expired 1 minute ago
    }
    expired_token = jwt.encode(expired_token_data, secret_key, algorithm=algorithm)
    
    response = client.post("/auth/refresh", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_refresh_token_malformed(client: TestClient):
    """Test refresh with malformed token"""
    response = client.post("/auth/refresh", headers={"Authorization": "Bearer not.a.jwt"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_refresh_token_user_not_found(client: TestClient, db_session: AsyncSession):
    """Test refresh with valid token but user deleted from database"""
    # Register user and get token
    client.post("/auth/register", json={"username": "testuser", "password": "securepassword"})
    login_response = client.post("/auth/login", json={"username": "testuser", "password": "securepassword"})
    access_token = login_response.json()["access_token"]
    
    # Delete user from database
    result = await db_session.execute(select(User).where(User.username == "testuser"))
    user = result.scalar_one_or_none()
    if user:
        await db_session.delete(user)
        await db_session.commit()
    
    # Try to refresh - should fail
    response = client.post("/auth/refresh", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_password_hashing_security(client: TestClient, db_session: AsyncSession):
    """Test that passwords are properly hashed and salted"""
    # Register two users with same password
    client.post("/auth/register", json={"username": "user1", "password": "samepassword"})
    client.post("/auth/register", json={"username": "user2", "password": "samepassword"})
    
    # Get both users from database
    result1 = await db_session.execute(select(User).where(User.username == "user1"))
    user1 = result1.scalar_one_or_none()
    
    result2 = await db_session.execute(select(User).where(User.username == "user2"))
    user2 = result2.scalar_one_or_none()
    
    # Password hashes should be different (due to salt)
    assert user1.password_hash != user2.password_hash
    # Both should be different from plain password
    assert user1.password_hash != "samepassword"
    assert user2.password_hash != "samepassword"