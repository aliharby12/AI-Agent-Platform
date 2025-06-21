from app.api.dependencies import get_db_session
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Agent
from app.api.schemas import AgentCreate, AgentResponse

router = APIRouter()

@router.post("/agents", response_model=AgentResponse)
async def create_agent(agent: AgentCreate, db: AsyncSession = Depends(get_db_session)):
    db_agent = Agent(name=agent.name, prompt=agent.prompt)
    db.add(db_agent)
    await db.commit()
    await db.refresh(db_agent)
    return db_agent