from openai import AsyncOpenAI
from app.models.models import Agent, ChatSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def generate_chat_response(
    client: AsyncOpenAI, db: AsyncSession, session_id: int, user_message: str
) -> str:
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