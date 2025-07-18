from pydantic import BaseModel
from datetime import datetime

class ChatSessionCreate(BaseModel):
    agent_id: int

class ChatSessionResponse(BaseModel):
    id: int
    agent_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    session_id: int
    content: str
    is_user: bool
    created_at: datetime
    audio_url: str | None = None

    model_config = {"from_attributes": True}

class MessageResponseWithAgent(MessageResponse):
    agent_name: str

class VoiceResponse(BaseModel):
    user_message: MessageResponse
    agent_message: MessageResponse
    agent_audio_url: str | None = None