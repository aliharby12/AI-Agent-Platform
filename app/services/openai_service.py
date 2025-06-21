from openai import AsyncOpenAI
from app.models.agent import Agent
from app.models.chat import ChatSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import aiofiles
import os
import uuid
import logging

logger = logging.getLogger(__name__)

async def generate_chat_response(
    client: AsyncOpenAI, db: AsyncSession, session_id: int, user_message: str
) -> str:
    """
    Generate a chat response using OpenAI API.
    
    Args:
        client (AsyncOpenAI): OpenAI client
        db (AsyncSession): Database session
        session_id (int): Chat session ID
        user_message (str): User's message
        
    Returns:
        str: Generated response from the agent
        
    Raises:
        ValueError: If session or agent not found
        Exception: For other errors during API call
    """
    try:
        # Retrieve session and associated agent
        result = await db.execute(
            select(ChatSession).filter(ChatSession.id == session_id)
        )
        session = result.scalars().first()
        if not session:
            raise ValueError("Session not found")
        result = await db.execute(select(Agent).filter(Agent.id == session.agent_id))
        agent = result.scalars().first()
        if not agent:
            raise ValueError("Agent not found")

        # Call OpenAI API
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": agent.prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content
    except ValueError as e:
        logger.error(f"Value error in generate_chat_response: {e}")
        raise
    except Exception as e:
        logger.error(f"Error generating chat response: {e}")
        raise Exception(f"Failed to generate response: {str(e)}")


async def transcribe_audio(client: AsyncOpenAI, audio_path: str) -> str:
    """
    Transcribe audio file using OpenAI Whisper API.
    
    Args:
        client (AsyncOpenAI): OpenAI client
        audio_path (str): Path to audio file
        
    Returns:
        str: Transcribed text
        
    Raises:
        Exception: For errors during transcription
    """
    try:
        # Read audio file as bytes
        async with aiofiles.open(audio_path, "rb") as audio_file:
            audio_content = await audio_file.read()
        
        # Transcribe audio using OpenAI Whisper
        transcription = await client.audio.transcriptions.create(
            model="whisper-1",
            file=(os.path.basename(audio_path), audio_content, "audio/mpeg")
        )
        return transcription.text
    except Exception as e:
        logger.error(f"Error transcribing audio {audio_path}: {e}")
        raise Exception(f"Failed to transcribe audio: {str(e)}")

async def generate_voice_response(
    client: AsyncOpenAI, text: str, session_id: int
) -> str:
    """
    Generate voice response using OpenAI TTS API.
    
    Args:
        client (AsyncOpenAI): OpenAI client
        text (str): Text to convert to speech
        session_id (int): Session ID for file naming
        
    Returns:
        str: Path to generated audio file
        
    Raises:
        Exception: For errors during voice generation
    """
    try:
        # Generate unique filename for audio
        audio_filename = f"static/audio_{session_id}_{uuid.uuid4().hex}.mp3"
        os.makedirs("static", exist_ok=True)

        # Generate speech using OpenAI TTS
        response = await client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )

        # Save audio file asynchronously
        async with aiofiles.open(audio_filename, "wb") as f:
            await f.write(response.content)

        return audio_filename
    except Exception as e:
        logger.error(f"Error generating voice response: {e}")
        raise Exception(f"Failed to generate voice response: {str(e)}")