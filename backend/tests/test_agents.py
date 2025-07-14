import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.models.agent import Agent

@pytest.mark.asyncio
async def test_create_agent(client: TestClient, access_token: str):
    response = client.post(
        "/api/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestAgent"
    assert data["prompt"] == "You are a helpful assistant"
    assert "id" in data
    assert "created_at" in data

@pytest.mark.asyncio
async def test_create_agent_missing_fields(client: TestClient, access_token: str):
    response = client.post(
        "/api/agents/",
        json={"name": "TestAgent"},  # Missing prompt
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_agent_unauthorized(client: TestClient):
    response = client.post("/api/agents/", json={"name": "TestAgent", "prompt": "You are a helpful assistant"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_agent_invalid_token(client: TestClient):
    response = client.post(
        "/api/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_list_agents_empty(client: TestClient, access_token: str):
    response = client.get("/api/agents/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

@pytest.mark.asyncio
async def test_list_agents_multiple(client: TestClient, access_token: str):
    # Create multiple agents
    agents_data = [
        {"name": "Agent1", "prompt": "You are agent 1"},
        {"name": "Agent2", "prompt": "You are agent 2"},
        {"name": "Agent3", "prompt": "You are agent 3"}
    ]
    
    for agent_data in agents_data:
        client.post(
            "/api/agents/",
            json=agent_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
    
    response = client.get("/api/agents/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # Verify agents are in order (assuming they're ordered by creation)
    agent_names = [agent["name"] for agent in data]
    assert "Agent1" in agent_names
    assert "Agent2" in agent_names
    assert "Agent3" in agent_names

@pytest.mark.asyncio
async def test_get_agent_exists(client: TestClient, access_token: str):
    create_response = client.post(
        "/api/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    agent_id = create_response.json()["id"]
    
    response = client.get(f"/api/agents/{agent_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == agent_id
    assert data["name"] == "TestAgent"
    assert data["prompt"] == "You are a helpful assistant"

@pytest.mark.asyncio
async def test_get_agent_not_found(client: TestClient, access_token: str):
    response = client.get("/api/agents/999", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Agent not found"}

@pytest.mark.asyncio
async def test_get_agent_invalid_id(client: TestClient, access_token: str):
    response = client.get("/api/agents/invalid", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 422  # Validation error for invalid ID format

@pytest.mark.asyncio
async def test_update_agent_name_only(client: TestClient, access_token: str):
    create_response = client.post(
        "/api/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    agent_id = create_response.json()["id"]
    
    response = client.patch(
        f"/api/agents/{agent_id}",
        json={"name": "UpdatedAgent"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "UpdatedAgent"
    assert data["prompt"] == "You are a helpful assistant"  # Should remain unchanged

@pytest.mark.asyncio
async def test_update_agent_prompt_only(client: TestClient, access_token: str):
    create_response = client.post(
        "/api/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    agent_id = create_response.json()["id"]
    
    response = client.patch(
        f"/api/agents/{agent_id}",
        json={"prompt": "You are an updated assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestAgent"  # Should remain unchanged
    assert data["prompt"] == "You are an updated assistant"

@pytest.mark.asyncio
async def test_update_agent_both_fields(client: TestClient, access_token: str):
    create_response = client.post(
        "/api/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    agent_id = create_response.json()["id"]
    
    response = client.patch(
        f"/api/agents/{agent_id}",
        json={"name": "UpdatedAgent", "prompt": "You are an updated assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "UpdatedAgent"
    assert data["prompt"] == "You are an updated assistant"

@pytest.mark.asyncio
async def test_update_agent_empty_body(client: TestClient, access_token: str):
    create_response = client.post(
        "/api/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    agent_id = create_response.json()["id"]
    
    response = client.patch(
        f"/api/agents/{agent_id}",
        json={},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    # Should remain unchanged
    assert data["name"] == "TestAgent"
    assert data["prompt"] == "You are a helpful assistant"

@pytest.mark.asyncio
async def test_update_agent_not_found(client: TestClient, access_token: str):
    response = client.patch(
        "/api/agents/999",
        json={"name": "UpdatedAgent"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Agent not found"}

@pytest.mark.asyncio
async def test_delete_agent_exists(client: TestClient, access_token: str, db_session: AsyncSession):
    create_response = client.post(
        "/api/agents/",
        json={"name": "TestAgent", "prompt": "You are a helpful assistant"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    agent_id = create_response.json()["id"]
    
    response = client.delete(f"/api/agents/{agent_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    
    # Verify the response contains the deleted agent data
    data = response.json()
    assert data["id"] == agent_id
    assert data["name"] == "TestAgent"
    
    # Verify deletion from database
    result = await db_session.execute(select(Agent).where(Agent.id == agent_id))
    assert result.scalar_one_or_none() is None

@pytest.mark.asyncio
async def test_delete_agent_not_found(client: TestClient, access_token: str):
    response = client.delete("/api/agents/999", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Agent not found"}

@pytest.mark.asyncio
async def test_agent_endpoints_unauthorized(client: TestClient):
    """Test all agent endpoints without authentication"""
    endpoints = [
        ("GET", "/api/agents/"),
        ("GET", "/api/agents/1"),
        ("PATCH", "/api/agents/1"),
        ("DELETE", "/api/agents/1")
    ]
    
    for method, endpoint in endpoints:
        if method == "GET":
            response = client.get(endpoint)
        elif method == "PATCH":
            response = client.patch(endpoint, json={"name": "Test"})
        elif method == "DELETE":
            response = client.delete(endpoint)
        
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_agent_with_long_name_and_prompt(client: TestClient, access_token: str):
    """Test creating agent with very long name and prompt"""
    long_name = "A" * 1000
    long_prompt = "B" * 5000
    
    response = client.post(
        "/api/agents/",
        json={"name": long_name, "prompt": long_prompt},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == long_name
    assert data["prompt"] == long_prompt

@pytest.mark.asyncio
async def test_agent_with_special_characters(client: TestClient, access_token: str):
    """Test creating agent with special characters in name and prompt"""
    special_name = "Test Agent @#$%^&*()"
    special_prompt = "You are a helpful assistant! Handle these chars: <>\"'&"
    
    response = client.post(
        "/api/agents/",
        json={"name": special_name, "prompt": special_prompt},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == special_name
    assert data["prompt"] == special_prompt