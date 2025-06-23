from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from .base import Base
from sqlalchemy.orm import relationship

class User(Base):
    """Model for users in the AI Agent Platform."""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    agents = relationship("Agent", back_populates="user", cascade="all, delete-orphan")