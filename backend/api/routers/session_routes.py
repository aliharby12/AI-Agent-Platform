from typing import List, Optional
from backend.api.schemas.chat import MessageCreate, MessageResponse, MessageResponseWithAgent, VoiceResponse
from backend.services.openai_service import generate_chat_response, generate_voice_response, transcribe_audio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.agent import Agent
from backend.models.chat import ChatSession, Message
from backend.models.user import User
from backend.api.schemas import ChatSessionCreate, ChatSessionResponse
from backend.api.dependencies import get_db_session, get_openai_client, get_current_user, security_scheme
from sqlalchemy.future import select
from openai import AsyncOpenAI
import aiofiles
import os
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("/", response_model=ChatSessionResponse)
async def create_session(
    session: ChatSessionCreate, 
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security_scheme)
):
    """
    Create a new chat session for an agent.
    Args:
        session (ChatSessionCreate): The session data containing agent_id
        db (AsyncSession): Database session dependency
        current_user (User): Current authenticated user
        token (str): JWT Bearer token
    Returns:
        ChatSessionResponse: The created chat session with its ID and other details
    Raises:
        HTTPException: If the agent does not exist or if there's an error during database operations
    """
    try:
        result = await db.execute(select(Agent).filter(Agent.id == session.agent_id, Agent.user_id == current_user.id))
        if not result.scalars().first():
            raise HTTPException(status_code=404, detail="Agent not found or not owned by user")
        db_session = ChatSession(agent_id=session.agent_id)
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        return db_session
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=400, detail="Failed to create session. Please try again.")


@router.post("/{session_id}/messages", response_model=MessageResponseWithAgent)
async def send_message(
    session_id: int,
    message: MessageCreate,
    db: AsyncSession = Depends(get_db_session),
    client: AsyncOpenAI = Depends(get_openai_client),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security_scheme)
):
    """
    Send a message to a chat session and receive a response from the agent.
    Args:
        session_id (int): The ID of the chat session
        message (MessageCreate): The message to send
        db (AsyncSession): Database session dependency
        client (AsyncOpenAI): OpenAI client dependency
        current_user (User): Current authenticated user
        token (str): JWT Bearer token
    Returns:
        MessageResponseWithAgent: The response message from the agent, including agent details
    Raises:
        HTTPException: If the session does not exist or if there's an error during database operations
    """
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error sending message to session {session_id}: {e}")
        raise HTTPException(status_code=400, detail="Failed to send message. Please try again.")


@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    session_id: int, 
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security_scheme)
):
    """
    Retrieve all messages from a chat session.
    Args:
        session_id (int): The ID of the chat session
        db (AsyncSession): Database session dependency
        current_user (User): Current authenticated user
        token (str): JWT Bearer token
    Returns:
        list[MessageResponseWithAgent]: List of messages in the session with agent details
    Raises:
        HTTPException: If the session does not exist or if there's an error during database operations
    """
    try:
        result = await db.execute(select(ChatSession).filter(ChatSession.id == session_id))
        if not result.scalars().first():
            raise HTTPException(status_code=404, detail="Session not found")

        # Retrieve messages for the session
        result = await db.execute(
            select(Message).filter(Message.session_id == session_id).order_by(Message.created_at)
        )
        messages = result.scalars().all()
        return messages
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving messages for session {session_id}: {e}")
        raise HTTPException(status_code=400, detail="Failed to retrieve messages. Please try again.")


@router.post("/{session_id}/voice", response_model=VoiceResponse)
async def send_voice_message(
    session_id: int,
    audio: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    client: AsyncOpenAI = Depends(get_openai_client),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security_scheme)
):
    """
    Send a voice message to a chat session and receive a response from the agent.
    Args:
        session_id (int): The ID of the chat session
        audio (UploadFile): The audio file to transcribe
        db (AsyncSession): Database session dependency
        client (AsyncOpenAI): OpenAI client dependency
        current_user (User): Current authenticated user
        token (str): JWT Bearer token
    Returns:
        VoiceResponse: The response message and audio URL from the agent
    Raises:
        HTTPException: If the session does not exist or if there's an error during processing
    """
    try:
        # Verify session exists
        result = await db.execute(select(ChatSession).filter(ChatSession.id == session_id))
        session = result.scalars().first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Validate audio file type
        if audio.content_type not in ["audio/mpeg", "audio/wav"]:
            raise HTTPException(status_code=400, detail="Invalid audio format. Use MP3 or WAV.")

        # Save uploaded audio file
        os.makedirs("uploads", exist_ok=True)
        audio_filename = f"uploads/audio_{session_id}_{uuid.uuid4().hex}.{audio.filename.split('.')[-1]}"
        async with aiofiles.open(audio_filename, "wb") as f:
            await f.write(await audio.read())

        # Transcribe audio to text
        try:
            user_message_text = await transcribe_audio(client, audio_filename)
        except Exception as e:
            logger.error(f"Transcription failed for session {session_id}: {e}")
            raise HTTPException(status_code=400, detail="Failed to transcribe audio. Please try again.")

        # Save transcribed user message
        user_message = Message(session_id=session_id, content=user_message_text, is_user=True)
        db.add(user_message)
        await db.commit()
        await db.refresh(user_message)

        # Generate text response
        agent_response_content = await generate_chat_response(client, db, session_id, user_message_text)
        agent_message = Message(session_id=session_id, content=agent_response_content, is_user=False)
        db.add(agent_message)
        await db.commit()
        await db.refresh(agent_message)

        # Generate voice response
        try:
            audio_filename = await generate_voice_response(client, agent_response_content, session_id)
            audio_url = f"/static/{audio_filename.split('/')[-1]}"
        except Exception as e:
            logger.error(f"Voice generation failed for session {session_id}: {e}")
            # Return text response even if voice generation fails
            audio_url = None

        return {
            "message": agent_message,
            "audio_url": audio_url
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error processing voice message for session {session_id}: {e}")
        raise HTTPException(status_code=400, detail="Failed to process voice message. Please try again.")
    

@router.delete("/{session_id}", status_code=204)
async def delete_session(
    session_id: int, 
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security_scheme)
):
    """
    Delete a chat session and all associated messages.
    Args:
        session_id (int): The ID of the chat session to delete
        db (AsyncSession): Database session dependency
        current_user (User): Current authenticated user
        token (str): JWT Bearer token
    Returns:
        None: No content response on successful deletion
    Raises:
        HTTPException: If the session does not exist or if there's an error during deletion
    """
    # Verify session exists
    result = await db.execute(select(ChatSession).filter(ChatSession.id == session_id))
    db_session = result.scalars().first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Delete session (messages are deleted via cascade)
    await db.delete(db_session)
    await db.commit()

@router.get("/", response_model=List[ChatSessionResponse])
async def list_sessions(
    agent_id: Optional[int] = None, 
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    token: str = Depends(security_scheme)
):
    """
    List all chat sessions, optionally filtered by agent_id.
    Args:
        agent_id (Optional[int]): The ID of the agent to filter sessions by
        db (AsyncSession): Database session dependency
        current_user (User): Current authenticated user
        token (str): JWT Bearer token
    Returns:
        List[ChatSessionResponse]: List of chat sessions, optionally filtered by agent_id
    Raises:
        HTTPException: If there's an error during database operations
    """
    # Retrieve sessions, optionally filtered by agent_id
    query = select(ChatSession)
    if agent_id is not None:
        query = query.filter(ChatSession.agent_id == agent_id)
    result = await db.execute(query.order_by(ChatSession.created_at))
    sessions = result.scalars().all()
    return sessions