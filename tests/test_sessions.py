import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from unittest.mock import patch
from app.models.chat import ChatSession, Message

@pytest.mark.asyncio
async def test_create_session(client: TestClient, access_token: str):
    client.post(
        "/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    response = client.post(
        "/sessions/",
        json={"agent_id": 1},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == 1
    assert "id" in data

@pytest.mark.asyncio
async def test_send_message(client: TestClient, access_token: str):
    client.post(
        "/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    session_response = client.post(
        "/sessions/",
        json={"agent_id": 1},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    session_id = session_response.json()["id"]
    response = client.post(
        f"/sessions/{session_id}/messages",
        json={"content": "Hello"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Mocked response"
    assert data["is_user"] is False
    assert data["agent_name"] == "TestAgent"

@pytest.mark.asyncio
async def test_voice_message(client: TestClient, access_token: str, db_session: AsyncSession):
    client.post(
        "/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    session_response = client.post(
        "/sessions/",
        json={"agent_id": 1},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    session_id = session_response.json()["id"]

    with patch("os.path.exists", return_value=True), patch("os.makedirs", return_value=None):
        response = client.post(
            f"/sessions/{session_id}/voice",
            files={"audio": ("test_audio.mp3", b"mocked audio", "audio/mpeg")},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"]["content"] == "Mocked response"
        assert data["message"]["is_user"] is False
        assert data["audio_url"].startswith("/static/audio_")

        # Note: The audio_files table doesn't exist in our current schema
        # This test would need to be updated based on the actual audio file storage implementation

@pytest.mark.asyncio
async def test_delete_session_with_audio_cleanup(client: TestClient, access_token: str, db_session: AsyncSession):
    client.post(
        "/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    session_response = client.post(
        "/sessions/",
        json={"agent_id": 1},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    session_id = session_response.json()["id"]

    with patch("os.path.exists", return_value=True), patch("os.makedirs", return_value=None), patch("os.remove", return_value=None):
        client.post(
            f"/sessions/{session_id}/voice",
            files={"audio": ("test_audio.mp3", b"mocked audio", "audio/mpeg")},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response = client.delete(f"/sessions/{session_id}", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 204

        # Verify session and messages are deleted using SQLAlchemy ORM
        result = await db_session.execute(select(ChatSession).where(ChatSession.id == session_id))
        assert result.scalar_one_or_none() is None
        
        result = await db_session.execute(select(Message).where(Message.session_id == session_id))
        assert result.scalars().all() == []
        
        # Note: audio_files table doesn't exist in current schema