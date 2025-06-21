from app.models.user import User
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent import Agent
from app.api.schemas import AgentCreate, AgentUpdate, AgentResponse
from app.api.dependencies import get_current_user, get_db_session, security_scheme
from sqlalchemy.future import select
from typing import List

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.post("/", response_model=AgentResponse)
async def create_agent(
    agent: AgentCreate, 
    db: AsyncSession = Depends(get_db_session), 
    current_user: User = Depends(get_current_user),
    token: str = Depends(security_scheme)
):
    """
    Create a new agent in the database.
    
    Args:
        agent (AgentCreate): The agent data containing name and prompt
        db (AsyncSession): Database session dependency
        current_user (User): Current authenticated user
        token (str): JWT Bearer token
        
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

@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security_scheme)
):
    """
    Retrieve all agents from the database.
    
    Args:
        db (AsyncSession): Database session dependency
        current_user (User): Current authenticated user
        token (str): JWT Bearer token
        
    Returns:
        List[AgentResponse]: List of all agents in the database
        
    Raises:
        HTTPException: If there's an error during database operations
    """
    result = await db.execute(select(Agent))
    return result.scalars().all()

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int, 
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security_scheme)
):
    """
    Retrieve a specific agent by its ID.
    
    Args:
        agent_id (int): The unique identifier of the agent
        db (AsyncSession): Database session dependency
        current_user (User): Current authenticated user
        token (str): JWT Bearer token
        
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

@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int, 
    agent: AgentUpdate, 
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security_scheme)
):
    """
    Update an existing agent's information.
    
    Args:
        agent_id (int): The unique identifier of the agent to update
        agent (AgentUpdate): The updated agent data (name and/or prompt)
        db (AsyncSession): Database session dependency
        current_user (User): Current authenticated user
        token (str): JWT Bearer token
        
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

@router.delete("/{agent_id}", response_model=AgentResponse)
async def delete_agent(
    agent_id: int, 
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security_scheme)
):
    """
    Delete an agent from the database.
    
    Args:
        agent_id (int): The unique identifier of the agent to delete
        db (AsyncSession): Database session dependency
        current_user (User): Current authenticated user
        token (str): JWT Bearer token
        
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