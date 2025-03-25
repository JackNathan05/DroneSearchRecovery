# src/repositories/user_repository.py
import logging
from datetime import datetime
from src.repositories.base_repository import BaseRepository
from src.models.user import User

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository):
    """Repository for User operations"""
    
    def __init__(self, session):
        super().__init__(session, User)
    
    def get_by_username(self, username):
        """Get user by username"""
        return self.session.query(User).filter(User.username == username).first()
    
    def create_user(self, username, password, is_admin=False):
        """Create a new user"""
        # Check if username already exists
        if self.get_by_username(username):
            logger.warning(f"User creation failed: Username '{username}' already exists")
            return None
        
        # Create new user
        user = User(
            username=username,
            password_hash=User.hash_password(password),
            is_admin=is_admin
        )
        
        return self.add(user)
    
    def authenticate(self, username, password):
        """Authenticate a user"""
        user = self.get_by_username(username)
        
        if not user:
            logger.warning(f"Authentication failed: User '{username}' not found")
            return None
        
        if not User.verify_password(user.password_hash, password):
            logger.warning(f"Authentication failed: Invalid password for user '{username}'")
            return None
        
        # Update last login timestamp
        user.last_login = datetime.utcnow()
        self.update(user)
        
        return user