from app.api.schemas.chat import MessageCreate, MessageResponseWithAgent
from app.services.openai_service import generate_chat_response
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Agent, ChatSession, Message
from app.api.schemas import ChatSessionCreate, ChatSessionResponse
from app.api.dependencies import get_db_session, get_openai_client
from sqlalchemy.future import select
from openai import AsyncOpenAI


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


@router.post("/{session_id}/messages", response_model=MessageResponseWithAgent)
async def send_message(
    session_id: int,
    message: MessageCreate,
    db: AsyncSession = Depends(get_db_session),
    client: AsyncOpenAI = Depends(get_openai_client)
):
    """
    Send a message to a chat session and receive a response from the agent.
    Args:
        session_id (int): The ID of the chat session
        message (MessageCreate): The message to send
        db (AsyncSession): Database session dependency
        client (AsyncOpenAI): OpenAI client dependency
    Returns:
        MessageResponseWithAgent: The response message from the agent, including agent details
    Raises:
        HTTPException: If the session does not exist or if there's an error during database operations
    """
    # Verify session exists
    result = await db.execute(select(ChatSession).filter(ChatSession.id == session_id))
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Save user message
    user_message = Message(session_id=session_id, content=message.content, is_user=True)
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)

    # Generate and save agent response
    agent_response_content = await generate_chat_response(client, db, session_id, message.content)
    agent_message = Message(session_id=session_id, content=agent_response_content, is_user=False)
    db.add(agent_message)
    await db.commit()
    await db.refresh(agent_message)

    # Fetch agent details for response
    result = await db.execute(select(Agent).filter(Agent.id == session.agent_id))
    agent = result.scalars().first()

    return {
        "id": agent_message.id,
        "session_id": agent_message.session_id,
        "content": agent_message.content,
        "is_user": agent_message.is_user,
        "created_at": agent_message.created_at,
        "agent_name": agent.name
    }