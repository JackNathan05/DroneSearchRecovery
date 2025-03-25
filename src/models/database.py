# src/models/database.py
import os
import logging
import sqlite3
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

logger = logging.getLogger(__name__)

# Create base class for declarative models - THIS MUST BE IMPORTED BY ALL MODELS
Base = declarative_base()

class Database:
    """Database connection manager"""
    
    def __init__(self, db_path="data/drone_search.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.engine = None
        self.Session = None
        self._ensure_directory()
        self._create_engine()
    
    def _ensure_directory(self):
        """Ensure the database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _create_engine(self):
        """Create SQLAlchemy engine and session factory"""
        # SQLite URL format: sqlite:///path/to/file.db
        db_url = f"sqlite:///{self.db_path}"
        
        # Create engine
        self.engine = create_engine(
            db_url,
            echo=False,
        )
        
        # Create session factory
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        
        logger.info(f"Database engine created at {self.db_path}")
    
    def create_tables(self):
        """Create all defined tables"""
        # Import all models here to ensure they're registered with Base
        # This avoids circular imports
        from src.models.user import User
        from src.models.mission import Mission, MissionBoundary
        from src.models.chat import ChatMessage
        from src.models.flight_plan import FlightPlan
        from src.models.weather import WeatherData
        
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created")
    
    def get_session(self):
        """Get a database session"""
        return self.Session()
    
    def backup(self, backup_path=None):
        """Create a backup of the database"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/backup/drone_search_{timestamp}.db"
        
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        # Close connections to ensure all data is flushed
        self.engine.dispose()
        
        # Use SQLite's backup functionality
        source = sqlite3.connect(self.db_path)
        dest = sqlite3.connect(backup_path)
        source.backup(dest)
        
        source.close()
        dest.close()
        
        # Recreate engine and session
        self._create_engine()
        
        logger.info(f"Database backed up to {backup_path}")
        return backup_path