import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.models.agent import Agent

@pytest.mark.asyncio
async def test_create_agent(client: TestClient, access_token: str):
    response = client.post(
        "/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestAgent"
    assert data["prompt"] == "You are a helpful assistant"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_agent_unauthorized(client: TestClient):
    response = client.post("/agents/", json={"name": "TestAgent", "prompt": "You are a helpful assistant"})
    assert response.status_code == 401
    # The actual error message might vary, so we just check for 401

@pytest.mark.asyncio
async def test_list_agents(client: TestClient, access_token: str):
    client.post(
        "/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    response = client.get("/agents/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "TestAgent"

@pytest.mark.asyncio
async def test_update_agent(client: TestClient, access_token: str):
    create_response = client.post(
        "/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    agent_id = create_response.json()["id"]
    response = client.patch(
        f"/agents/{agent_id}",
        json={"name": "UpdatedAgent", "prompt": "You are an updated assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "UpdatedAgent"
    assert data["prompt"] == "You are an updated assistant"

@pytest.mark.asyncio
async def test_delete_agent(client: TestClient, access_token: str, db_session: AsyncSession):
    create_response = client.post(
        "/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    agent_id = create_response.json()["id"]
    response = client.delete(f"/agents/{agent_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200  # Our delete endpoint returns 200 with the deleted agent

    # Verify deletion using SQLAlchemy ORM
    from sqlalchemy.future import select
    result = await db_session.execute(select(Agent).where(Agent.id == agent_id))
    assert result.scalar_one_or_none() is None