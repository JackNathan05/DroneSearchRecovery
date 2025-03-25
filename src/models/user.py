# src/models/user.py
import hashlib
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from src.models.database import Base

class User(Base):
    """User model for authentication and identification"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_admin = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<User(username='{self.username}')>"
    
    @staticmethod
    def hash_password(password):
        """Hash a password using SHA-256 (for demonstration only)
        
        Note: In a real application, use a proper password hashing library
        like bcrypt, argon2, or pbkdf2.
        """
        # Add a salt for improved security
        salt = uuid.uuid4().hex
        # Hash the salted password
        return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify a password against its hash
        
        Note: This is for demonstration only. Use proper password
        verification in production.
        """
        hash_part, salt = stored_password.split(':')
        return hash_part == hashlib.sha256(salt.encode() + provided_password.encode()).hexdigest()