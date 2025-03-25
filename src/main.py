# src/main.py
import sys
import os
# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from PyQt6.QtWidgets import QApplication
from src.utils.backup_manager import BackupManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Application entry point"""
    logger.info("Starting Drone Search & Recovery Application")
    
    # Import here to avoid circular imports
    from src.models.database import Database
    from src.repositories.user_repository import UserRepository
    
    # Initialize database
    db = Database()
    db.create_tables()  # This will import all models
    
    # Create default users if they don't exist
    session = db.get_session()
    user_repo = UserRepository(session)
    
    try:
        if not user_repo.get_by_username("admin"):
            user_repo.create_user("admin", "admin123", is_admin=True)
            logger.info("Created default admin user")
        
        if not user_repo.get_by_username("1"):
            user_repo.create_user("1", "1")
            logger.info("Created test user")
    except Exception as e:
        logger.error(f"Error creating default users: {e}")
    finally:
        session.close()

    # Initialize backup manager
    backup_manager = BackupManager(db)
    backup_manager.start_scheduled_backups()
    
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("Drone Search & Recovery")
    app.setApplicationVersion("0.1.0")
    
    # Import and create main window
    from src.views.main_window import MainWindow
    window = MainWindow(db)  # Pass db instance here
    window.show()
    
    logger.info("Application initialized and window displayed")

    # Handle application shutdown
    app.aboutToQuit.connect(lambda: backup_manager.stop_scheduled_backups())
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()