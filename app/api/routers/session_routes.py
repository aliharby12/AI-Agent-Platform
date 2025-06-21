from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Agent, ChatSession
from app.api.schemas import ChatSessionCreate, ChatSessionResponse
from app.api.dependencies import get_db_session
from sqlalchemy.future import select

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("/", response_model=ChatSessionResponse)
async def create_session(session: ChatSessionCreate, db: AsyncSession = Depends(get_db_session)):
    """
    Create a new chat session for an agent.
    Args:
        session (ChatSessionCreate): The session data containing agent_id
        db (AsyncSession): Database session dependency
    Returns:
        ChatSessionResponse: The created chat session with its ID and other details
    Raises:
        HTTPException: If the agent does not exist or if there's an error during database operations
    """
    result = await db.execute(select(Agent).filter(Agent.id == session.agent_id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Agent not found")
    db_session = ChatSession(agent_id=session.agent_id)
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session