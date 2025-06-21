from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Agent(Base):
    """Model for AI Agents."""
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatSession(Base):
    """Model for chat sessions associated with agents."""
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    """Model for messages exchanged in chat sessions."""
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    content = Column(String, nullable=False)
    is_user = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)