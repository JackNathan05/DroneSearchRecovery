# src/models/flight_plan.py
import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from src.models.database import Base

class FlightPlan(Base):
    """Model for storing drone flight plans"""
    
    __tablename__ = "flight_plans"
    
    id = Column(Integer, primary_key=True)
    mission_id = Column(Integer, ForeignKey("missions.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    pattern_type = Column(String(20), default="grid")  # grid, spiral, contour
    parameters = Column(Text, nullable=True)  # JSON string of flight parameters
    status = Column(String(20), default="draft")  # draft, ready, executed
    
    # Optional specific parameters
    altitude = Column(Float, nullable=True)  # in meters
    speed = Column(Float, nullable=True)  # in m/s
    overlap = Column(Float, nullable=True)  # as percentage
    camera_angle = Column(Float, nullable=True)  # in degrees
    
    # Relationship
    mission = relationship("Mission", back_populates="flight_plans")
    
    def __repr__(self):
        return f"<FlightPlan(pattern='{self.pattern_type}', status='{self.status}')>"
    
    def set_parameters(self, params_dict):
        """Set parameters from a dictionary"""
        self.parameters = json.dumps(params_dict)
    
    def get_parameters(self):
        """Get parameters as a dictionary"""
        if not self.parameters:
            return {}
        return json.loads(self.parameters)