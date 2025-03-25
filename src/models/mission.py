# src/models/mission.py
import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
import enum
from src.models.database import Base

class MissionStatus(enum.Enum):
    """Mission status enumeration"""
    NEW = "new"
    PLANNING = "planning"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Mission(Base):
    """Mission model for storing mission metadata"""
    
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(20), default=MissionStatus.NEW.value)
    mission_type = Column(String(20), default="custom")  # custom, imported
    description = Column(Text, nullable=True)
    
    # Relationships
    boundaries = relationship("MissionBoundary", back_populates="mission", cascade="all, delete-orphan")
    chat_history = relationship("ChatMessage", back_populates="mission", cascade="all, delete-orphan")
    flight_plans = relationship("FlightPlan", back_populates="mission", cascade="all, delete-orphan")
    weather_data = relationship("WeatherData", back_populates="mission", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Mission(name='{self.name}', status='{self.status}')>"

class MissionBoundary(Base):
    """Model for storing mission geographic boundaries"""
    
    __tablename__ = "mission_boundaries"
    
    id = Column(Integer, primary_key=True)
    mission_id = Column(Integer, ForeignKey("missions.id"))
    boundary_type = Column(String(20), default="polygon")  # polygon, circle, rectangle
    coordinates = Column(Text, nullable=False)  # JSON string of coordinates
    
    # Relationship
    mission = relationship("Mission", back_populates="boundaries")
    
    def __repr__(self):
        return f"<MissionBoundary(type='{self.boundary_type}')>"
    
    def set_coordinates(self, coords_list):
        """Set coordinates from a list/dict"""
        self.coordinates = json.dumps(coords_list)
    
    def get_coordinates(self):
        """Get coordinates as a list/dict"""
        return json.loads(self.coordinates)