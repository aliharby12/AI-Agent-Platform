from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AgentCreate(BaseModel):
    name: str
    prompt: str

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    prompt: Optional[str] = None

class AgentResponse(BaseModel):
    id: int
    name: str
    prompt: str
    created_at: datetime

    model_config = {"from_attributes": True}