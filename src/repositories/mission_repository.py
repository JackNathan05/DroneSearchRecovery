# src/repositories/mission_repository.py
import logging
from datetime import datetime
from src.repositories.base_repository import BaseRepository
from src.models.mission import Mission, MissionBoundary, MissionStatus
from src.models.chat import ChatMessage
from src.models.flight_plan import FlightPlan

logger = logging.getLogger(__name__)

class MissionRepository(BaseRepository):
    """Repository for Mission operations"""
    
    def __init__(self, session):
        super().__init__(session, Mission)
    
    def get_by_user(self, user_id):
        """Get all missions for a user"""
        return self.session.query(Mission).filter(Mission.user_id == user_id).all()
    
    def get_by_name_and_user(self, name, user_id):
        """Get mission by name and user"""
        return self.session.query(Mission).filter(
            Mission.name == name,
            Mission.user_id == user_id
        ).first()
    
    def create_mission(self, name, user_id, description=None, mission_type="custom"):
        """Create a new mission"""
        # Check if mission with same name already exists for user
        if self.get_by_name_and_user(name, user_id):
            logger.warning(f"Mission creation failed: Mission '{name}' already exists for user {user_id}")
            return None
        
        # Create new mission
        mission = Mission(
            name=name,
            user_id=user_id,
            description=description,
            mission_type=mission_type,
            status=MissionStatus.NEW.value
        )
        
        return self.add(mission)
    
    def update_status(self, mission_id, status):
        """Update mission status"""
        mission = self.get_by_id(mission_id)
        if not mission:
            logger.warning(f"Mission update failed: Mission {mission_id} not found")
            return None
        
        mission.status = status
        mission.updated_at = datetime.utcnow()
        
        return self.update(mission)
    
    def add_boundary(self, mission_id, boundary_type, coordinates):
        """Add a boundary to a mission"""
        mission = self.get_by_id(mission_id)
        if not mission:
            logger.warning(f"Boundary addition failed: Mission {mission_id} not found")
            return None
        
        boundary = MissionBoundary(
            mission_id=mission_id,
            boundary_type=boundary_type
        )
        boundary.set_coordinates(coordinates)
        
        self.session.add(boundary)
        self.session.commit()
        
        return boundary
    
    def add_chat_message(self, mission_id, message, sender_type="user", user_id=None):
        """Add a chat message to a mission"""
        chat_message = ChatMessage(
            mission_id=mission_id,
            user_id=user_id,
            sender_type=sender_type,
            message=message
        )
        
        self.session.add(chat_message)
        self.session.commit()
        
        return chat_message
    
    def get_chat_history(self, mission_id):
        """Get chat history for a mission"""
        return self.session.query(ChatMessage).filter(
            ChatMessage.mission_id == mission_id
        ).order_by(ChatMessage.timestamp).all()
    
    def add_flight_plan(self, mission_id, pattern_type, parameters=None):
        """Add a flight plan to a mission"""
        flight_plan = FlightPlan(
            mission_id=mission_id,
            pattern_type=pattern_type
        )
        
        if parameters:
            flight_plan.set_parameters(parameters)
        
        self.session.add(flight_plan)
        self.session.commit()
        
        return flight_plan
    
    def add_chat_message(self, mission_id, message, sender_type="user", user_id=None):
        """Add a chat message to a mission"""
        # Validate message is not None
        if message is None:
            logger.error("Cannot add None message to database")
            return None
            
        try:
            chat_message = ChatMessage(
                mission_id=mission_id,
                user_id=user_id,
                sender_type=sender_type,
                message=message
            )
            
            self.session.add(chat_message)
            self.session.commit()
            
            return chat_message
        except Exception as e:
            logger.error(f"Error adding chat message: {str(e)}")
            self.session.rollback()
            raise