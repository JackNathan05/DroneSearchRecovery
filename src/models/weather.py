# src/models/weather.py
import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from src.models.database import Base

class WeatherData(Base):
    """Model for storing weather data for missions"""
    
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True)
    mission_id = Column(Integer, ForeignKey("missions.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    data = Column(Text, nullable=True)  # JSON string of weather data
    
    # Optional specific parameters for quick access
    temperature = Column(Float, nullable=True)  # in Celsius
    wind_speed = Column(Float, nullable=True)  # in m/s
    wind_direction = Column(Float, nullable=True)  # in degrees
    precipitation = Column(Float, nullable=True)  # in mm
    
    # Relationship
    mission = relationship("Mission", back_populates="weather_data")
    
    def __repr__(self):
        return f"<WeatherData(timestamp='{self.timestamp}')>"
    
    def set_data(self, data_dict):
        """Set weather data from a dictionary"""
        self.data = json.dumps(data_dict)
        
        # Set specific parameters for quick access
        if "temperature" in data_dict:
            self.temperature = data_dict["temperature"]
        if "wind_speed" in data_dict:
            self.wind_speed = data_dict["wind_speed"]
        if "wind_direction" in data_dict:
            self.wind_direction = data_dict["wind_direction"]
        if "precipitation" in data_dict:
            self.precipitation = data_dict["precipitation"]
    
    def get_data(self):
        """Get weather data as a dictionary"""
        if not self.data:
            return {}
        return json.loads(self.data)