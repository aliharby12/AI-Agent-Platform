import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from unittest.mock import patch, MagicMock, AsyncMock
from app.models.chat import ChatSession, Message
from app.models.agent import Agent
import tempfile
import os

@pytest.mark.asyncio
async def test_create_session_success(client: TestClient, access_token: str, db_session: AsyncSession):
    # Create agent first
    agent_response = client.post(
        "/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    agent_id = agent_response.json()["id"]
    
    response = client.post(
        "/sessions/",
        json={"agent_id": agent_id},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == agent_id
    assert "id" in data
    assert "created_at" in data
    
    # Verify session exists in database
    result = await db_session.execute(select(ChatSession).where(ChatSession.id == data["id"]))
    session = result.scalar_one_or_none()
    assert session is not None
    assert session.agent_id == agent_id

@pytest.mark.asyncio
async def test_create_session_nonexistent_agent(client: TestClient, access_token: str):
    response = client.post(
        "/sessions/",
        json={"agent_id": 999},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Agent not found"}

@pytest.mark.asyncio
async def test_create_session_missing_agent_id(client: TestClient, access_token: str):
    response = client.post(
        "/sessions/",
        json={},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_session_invalid_agent_id(client: TestClient, access_token: str):
    response = client.post(
        "/sessions/",
        json={"agent_id": "invalid"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_session_unauthorized(client: TestClient):
    response = client.post("/sessions/", json={"agent_id": 1})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_send_message_success(client: TestClient, access_token: str, db_session: AsyncSession):
    # Setup agent and session
    agent_response = client.post(
        "/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    agent_id = agent_response.json()["id"]
    
    session_response = client.post(
        "/sessions/",
        json={"agent_id": agent_id},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    session_id = session_response.json()["id"]
    
    # Send message
    response = client.post(
        f"/sessions/{session_id}/messages",
        json={"content": "Hello, how are you?"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Mocked response"
    assert data["is_user"] is False
    assert data["agent_name"] == "TestAgent"
    assert data["session_id"] == session_id
    
    # Verify messages were saved to database
    result = await db_session.execute(select(Message).where(Message.session_id == session_id))
    messages = result.scalars().all()
    assert len(messages) == 2  # User message + agent response
    
    user_msg = next(msg for msg in messages if msg.is_user)
    agent_msg = next(msg for msg in messages if not msg.is_user)
    assert user_msg.content == "Hello, how are you?"
    assert agent_msg.content == "Mocked response"