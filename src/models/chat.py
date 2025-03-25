# src/models/chat.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.models.database import Base

class ChatMessage(Base):
    """Model for storing chat messages in missions"""
    
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True)
    mission_id = Column(Integer, ForeignKey("missions.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for system messages
    timestamp = Column(DateTime, default=datetime.utcnow)
    sender_type = Column(String(10), default="user")  # user, system
    message = Column(Text, nullable=False)
    
    # Relationships
    mission = relationship("Mission", back_populates="chat_history")
    
    def __repr__(self):
        return f"<ChatMessage(sender='{self.sender_type}', timestamp='{self.timestamp}')>"