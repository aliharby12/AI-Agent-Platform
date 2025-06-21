from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .base import Base

class User(Base):
    """Model for users in the AI Agent Platform."""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)