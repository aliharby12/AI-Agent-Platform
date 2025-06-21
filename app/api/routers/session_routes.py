from typing import List
from app.api.schemas.chat import MessageCreate, MessageResponse, MessageResponseWithAgent, VoiceResponse
from app.services.openai_service import generate_chat_response, generate_voice_response, transcribe_audio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Agent, ChatSession, Message
from app.api.schemas import ChatSessionCreate, ChatSessionResponse
from app.api.dependencies import get_db_session, get_openai_client
from sqlalchemy.future import select
from openai import AsyncOpenAI
import aiofiles
import os
import uuid
import logging

logger = logging.getLogger(__name__)

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
    try:
        result = await db.execute(select(Agent).filter(Agent.id == session.agent_id))
        if not result.scalars().first():
            raise HTTPException(status_code=404, detail="Agent not found")
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
async def get_messages(session_id: int, db: AsyncSession = Depends(get_db_session)):
    """
    Retrieve all messages from a chat session.
    Args:
        session_id (int): The ID of the chat session
        db (AsyncSession): Database session dependency
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
    client: AsyncOpenAI = Depends(get_openai_client)
):
    """
    Send a voice message to a chat session and receive a response from the agent.
    Args:
        session_id (int): The ID of the chat session
        audio (UploadFile): The audio file to transcribe
        db (AsyncSession): Database session dependency
        client (AsyncOpenAI): OpenAI client dependency
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