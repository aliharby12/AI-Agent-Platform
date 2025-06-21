from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Agent
from app.api.schemas import AgentCreate, AgentUpdate, AgentResponse
from app.api.dependencies import get_db_session
from sqlalchemy.future import select
from typing import List
from fastapi import HTTPException

router = APIRouter()

@router.post("/agents", response_model=AgentResponse)
async def create_agent(agent: AgentCreate, db: AsyncSession = Depends(get_db_session)):
    """
    Create a new agent in the database.
    
    Args:
        agent (AgentCreate): The agent data containing name and prompt
        db (AsyncSession): Database session dependency
        
    Returns:
        AgentResponse: The created agent with its ID and other details
        
    Raises:
        HTTPException: If there's an error during database operations
    """
    db_agent = Agent(name=agent.name, prompt=agent.prompt)
    db.add(db_agent)
    await db.commit()
    await db.refresh(db_agent)
    return db_agent

@router.get("/agents", response_model=List[AgentResponse])
async def list_agents(db: AsyncSession = Depends(get_db_session)):
    """
    Retrieve all agents from the database.
    
    Args:
        db (AsyncSession): Database session dependency
        
    Returns:
        List[AgentResponse]: List of all agents in the database
        
    Raises:
        HTTPException: If there's an error during database operations
    """
    result = await db.execute(select(Agent))
    return result.scalars().all()

@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: int, db: AsyncSession = Depends(get_db_session)):
    """
    Retrieve a specific agent by its ID.
    
    Args:
        agent_id (int): The unique identifier of the agent
        db (AsyncSession): Database session dependency
        
    Returns:
        AgentResponse: The agent with the specified ID
        
    Raises:
        HTTPException: 404 if agent is not found, or other database errors
    """
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.patch("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: int, agent: AgentUpdate, db: AsyncSession = Depends(get_db_session)):
    """
    Update an existing agent's information.
    
    Args:
        agent_id (int): The unique identifier of the agent to update
        agent (AgentUpdate): The updated agent data (name and/or prompt)
        db (AsyncSession): Database session dependency
        
    Returns:
        AgentResponse: The updated agent with its current information
        
    Raises:
        HTTPException: 404 if agent is not found, or other database errors
    """
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    db_agent = result.scalar_one_or_none()
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if agent.name is not None:
        db_agent.name = agent.name
    if agent.prompt is not None:
        db_agent.prompt = agent.prompt
    
    await db.commit()
    await db.refresh(db_agent)
    return db_agent

@router.delete("/agents/{agent_id}", response_model=AgentResponse)
async def delete_agent(agent_id: int, db: AsyncSession = Depends(get_db_session)):
    """
    Delete an agent from the database.
    
    Args:
        agent_id (int): The unique identifier of the agent to delete
        db (AsyncSession): Database session dependency
        
    Returns:
        AgentResponse: The deleted agent information (before deletion)
        
    Raises:
        HTTPException: 404 if agent is not found, or other database errors
    """
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    db_agent = result.scalar_one_or_none()
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    await db.delete(db_agent)
    await db.commit()
    return db_agent