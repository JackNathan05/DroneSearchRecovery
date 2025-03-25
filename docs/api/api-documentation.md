# API Documentation

This document provides documentation for the key APIs and classes in the Drone Search & Recovery application.

## Table of Contents

1. [Database Module](#database-module)
2. [Models](#models)
3. [Repositories](#repositories)
4. [UI Components](#ui-components)
5. [Utilities](#utilities)

---

## Database Module

### Database Class

**File**: `src/models/database.py`

The main database connection manager that handles engine creation, session management, and backup functionality.

```python
class Database:
    """Database connection manager"""
    
    def __init__(self, db_path="data/drone_search.db"):
        """Initialize database connection
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        # ...
    
    def create_tables(self):
        """Create all defined tables in the database"""
        # ...
    
    def get_session(self):
        """Get a database session
        
        Returns:
            Session: SQLAlchemy session object
        """
        # ...
    
    def backup(self, backup_path=None):
        """Create a backup of the database
        
        Args:
            backup_path (str, optional): Path for the backup file. If None, 
                                        a timestamped path is generated.
        
        Returns:
            str: Path to the created backup file
        """
        # ...
```

---

## Models

### User Model

**File**: `src/models/user.py`

User model for authentication and identification.

```python
class User(Base):
    """User model for authentication and identification"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_admin = Column(Boolean, default=False)
    
    @staticmethod
    def hash_password(password):
        """Hash a password using SHA-256 with salt
        
        Args:
            password (str): Plain text password
        
        Returns:
            str: Hashed password with salt
        """
        # ...
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify a password against its hash
        
        Args:
            stored_password (str): Stored password hash
            provided_password (str): Plain text password to verify
        
        Returns:
            bool: True if password matches, False otherwise
        """
        # ...
```

### Mission Model

**File**: `src/models/mission.py`

Mission model for storing mission metadata and related entities.

```python
class Mission(Base):
    """Mission model for storing mission metadata"""
    
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(20), default=MissionStatus.NEW.value)
    mission_type = Column(String(20), default="custom")
    description = Column(Text, nullable=True)
    
    # Relationships
    boundaries = relationship("MissionBoundary", back_populates="mission", cascade="all, delete-orphan")
    chat_history = relationship("ChatMessage", back_populates="mission", cascade="all, delete-orphan")
    flight_plans = relationship("FlightPlan", back_populates="mission", cascade="all, delete-orphan")
    weather_data = relationship("WeatherData", back_populates="mission", cascade="all, delete-orphan")
```

### Other Models

- **MissionBoundary** (`src/models/mission.py`): Stores geographic boundaries
- **ChatMessage** (`src/models/chat.py`): Stores chat history
- **FlightPlan** (`src/models/flight_plan.py`): Stores flight planning data
- **WeatherData** (`src/models/weather.py`): Stores weather information

---

## Repositories

### BaseRepository

**File**: `src/repositories/base_repository.py`

Base class for all repositories with common CRUD operations.

```python
class BaseRepository:
    """Base repository class for database operations"""
    
    def __init__(self, session, model_class):
        """Initialize with session and model class
        
        Args:
            session: SQLAlchemy session
            model_class: Model class to operate on
        """
        # ...
    
    def get_by_id(self, entity_id):
        """Get entity by ID
        
        Args:
            entity_id: Primary key of the entity
        
        Returns:
            Object or None: Found entity or None
        """
        # ...
    
    def get_all(self):
        """Get all entities
        
        Returns:
            list: All entities of this type
        """
        # ...
    
    def add(self, entity):
        """Add a new entity
        
        Args:
            entity: Entity to add
        
        Returns:
            Object: Added entity
        """
        # ...
    
    def update(self, entity):
        """Update an entity
        
        Args:
            entity: Entity to update
        
        Returns:
            Object: Updated entity
        """
        # ...
    
    def delete(self, entity):
        """Delete an entity
        
        Args:
            entity: Entity to delete
        """
        # ...
    
    def delete_by_id(self, entity_id):
        """Delete entity by ID
        
        Args:
            entity_id: Primary key of the entity
        
        Returns:
            bool: True if entity was deleted, False otherwise
        """
        # ...
```

### UserRepository

**File**: `src/repositories/user_repository.py`

Repository for user-related operations.

```python
class UserRepository(BaseRepository):
    """Repository for User operations"""
    
    def __init__(self, session):
        """Initialize with session
        
        Args:
            session: SQLAlchemy session
        """
        # ...
    
    def get_by_username(self, username):
        """Get user by username
        
        Args:
            username (str): Username to search for
        
        Returns:
            User or None: Found user or None
        """
        # ...
    
    def create_user(self, username, password, is_admin=False):
        """Create a new user
        
        Args:
            username (str): Username for new user
            password (str): Plain text password
            is_admin (bool, optional): Admin status. Defaults to False.
        
        Returns:
            User or None: Created user or None if username exists
        """
        # ...
    
    def authenticate(self, username, password):
        """Authenticate a user
        
        Args:
            username (str): Username to authenticate
            password (str): Plain text password
        
        Returns:
            User or None: Authenticated user or None
        """
        # ...
```

### MissionRepository

**File**: `src/repositories/mission_repository.py`

Repository for mission-related operations.

```python
class MissionRepository(BaseRepository):
    """Repository for Mission operations"""
    
    def __init__(self, session):
        """Initialize with session
        
        Args:
            session: SQLAlchemy session
        """
        # ...
    
    def get_by_user(self, user_id):
        """Get all missions for a user
        
        Args:
            user_id (int): User ID
        
        Returns:
            list: Missions belonging to the user
        """
        # ...
    
    def get_by_name_and_user(self, name, user_id):
        """Get mission by name and user
        
        Args:
            name (str): Mission name
            user_id (int): User ID
        
        Returns:
            Mission or None: Found mission or None
        """
        # ...
    
    def create_mission(self, name, user_id, description=None, mission_type="custom"):
        """Create a new mission
        
        Args:
            name (str): Mission name
            user_id (int): User ID
            description (str, optional): Mission description. Defaults to None.
            mission_type (str, optional): Mission type. Defaults to "custom".
        
        Returns:
            Mission or None: Created mission or None if name exists
        """
        # ...
    
    def update_status(self, mission_id, status):
        """Update mission status
        
        Args:
            mission_id (int): Mission ID
            status (str): New status
        
        Returns:
            Mission or None: Updated mission or None
        """
        # ...
    
    def add_boundary(self, mission_id, boundary_type, coordinates):
        """Add a boundary to a mission
        
        Args:
            mission_id (int): Mission ID
            boundary_type (str): Type of boundary
            coordinates: Coordinates data
        
        Returns:
            MissionBoundary or None: Created boundary or None
        """
        # ...
    
    def add_chat_message(self, mission_id, message, sender_type="user", user_id=None):
        """Add a chat message to a mission
        
        Args:
            mission_id (int): Mission ID
            message (str): Message content
            sender_type (str, optional): Sender type. Defaults to "user".
            user_id (int, optional): User ID. Defaults to None.
        
        Returns:
            ChatMessage: Created message
        """
        # ...
    
    def get_chat_history(self, mission_id):
        """Get chat history for a mission
        
        Args:
            mission_id (int): Mission ID
        
        Returns:
            list: Chat messages for the mission
        """
        # ...
    
    def add_flight_plan(self, mission_id, pattern_type, parameters=None):
        """Add a flight plan to a mission
        
        Args:
            mission_id (int): Mission ID
            pattern_type (str): Type of search pattern
            parameters (dict, optional): Flight parameters. Defaults to None.
        
        Returns:
            FlightPlan: Created flight plan
        """
        # ...
```

---

## UI Components

### MainWindow

**File**: `src/views/main_window.py`

Main application window with navigation and content management.

```python
class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, db):
        """Initialize with database
        
        Args:
            db: Database instance
        """
        # ...
    
    def setup_sidebar(self):
        """Set up the sidebar navigation menu"""
        # ...
    
    def setup_login_screen(self):
        """Set up the login screen"""
        # ...
    
    def setup_home_screen(self):
        """Set up the home screen with buttons"""
        # ...
    
    def setup_mission_planner_screen(self):
        """Set up the mission planner screen"""
        # ...
    
    def setup_mission_screen(self):
        """Set up the mission view screen"""
        # ...
    
    def handle_login(self, username):
        """Handle successful login
        
        Args:
            username (str): Authenticated username
        """
        # ...
    
    def load_user_missions(self, user_id):
        """Load missions for a user
        
        Args:
            user_id (int): User ID
        """
        # ...
    
    def go_to_home(self):
        """Navigate to home screen"""
        # ...
    
    def new_mission(self):
        """Create a new mission"""
        # ...
    
    def import_mission(self):
        """Import an existing mission"""
        # ...
    
    def open_mission(self, mission_name, button=None):
        """Open a specific mission
        
        Args:
            mission_name (str): Name of the mission
            button (QPushButton, optional): Button that was clicked. Defaults to None.
        """
        # ...
    
    def _rename_mission(self, mission_name, button):
        """Rename a mission
        
        Args:
            mission_name (str): Current mission name
            button (QPushButton): Button to update
        """
        # ...
    
    def _delete_mission(self, mission_name, button):
        """Delete a mission
        
        Args:
            mission_name (str): Mission name
            button (QPushButton): Button to remove
        """
        # ...
```

### LoginWidget

**File**: `src/views/login_view.py`

Login screen for user authentication.

```python
class LoginWidget(QWidget):
    """Login screen widget"""
    
    # Signal emitted on successful login
    login_successful = pyqtSignal(str)
    
    def __init__(self, user_repository):
        """Initialize with repository
        
        Args:
            user_repository: User repository instance
        """
        # ...
    
    def setup_ui(self):
        """Set up the user interface"""
        # ...
    
    def attempt_login(self):
        """Validate login credentials"""
        # ...
```

### MissionPlannerWidget

**File**: `src/views/mission_planner.py`

Widget for creating and configuring new missions.

```python
class MissionPlannerWidget(QWidget):
    """New mission planner screen widget"""
    
    # Signal to notify when a mission is created
    mission_created = pyqtSignal(str, str)
    
    def __init__(self):
        """Initialize the widget"""
        # ...
    
    def setup_ui(self):
        """Set up the user interface"""
        # ...
    
    def send_message(self):
        """Send a message to the chat"""
        # ...
    
    def simulate_response(self, message):
        """Simulate a response from the system
        
        Args:
            message (str): User message
        
        Returns:
            str: System response
        """
        # ...
    
    def cancel_mission(self):
        """Cancel mission creation"""
        # ...
    
    def create_mission(self):
        """Create the mission"""
        # ...
```

### MissionViewWidget

**File**: `src/views/mission_view.py`

Widget for displaying and interacting with missions.

```python
class MissionViewWidget(QWidget):
    """Mission view screen with chat and map"""
    
    def __init__(self, main_window=None):
        """Initialize with main window reference
        
        Args:
            main_window: MainWindow instance
        """
        # ...
    
    def setup_ui(self):
        """Set up the user interface"""
        # ...
    
    def set_mission_data(self, mission_name, mission_description):
        """Set mission data in the UI
        
        Args:
            mission_name (str): Mission name
            mission_description (str): Mission description
        """
        # ...
    
    def load_chat_history(self, mission_name):
        """Load chat history for a mission
        
        Args:
            mission_name (str): Mission name
        """
        # ...
    
    def send_message(self):
        """Send a message from the chat input"""
        # ...
    
    def simulate_response(self, message):
        """Simulate a response from the system
        
        Args:
            message (str): User message
        
        Returns:
            str: System response
        """
        # ...
```

---

## Utilities

### BackupManager

**File**: `src/utils/backup_manager.py`

Manages automatic backups of the database.

```python
class BackupManager:
    """Manages automatic backups of the database"""
    
    def __init__(self, database, config=None):
        """Initialize backup manager
        
        Args:
            database: Database instance
            config (dict, optional): Configuration options. Defaults to {}.
        """
        # ...
    
    def start_scheduled_backups(self):
        """Start scheduled backup thread"""
        # ...
    
    def stop_scheduled_backups(self):
        """Stop scheduled backup thread"""
        # ...
    
    def perform_backup(self):
        """Perform a database backup
        
        Returns:
            str: Path to created backup
        """
        # ...
    
    def _cleanup_old_backups(self):
        """Remove old backups if exceeding max_backups"""
        # ...
```

### Restore Utilities

**File**: `src/utils/restore_util.py`

Utilities for restoring from backups.

```python
def list_available_backups(backup_dir="data/backup"):
    """List available database backups
    
    Args:
        backup_dir (str, optional): Backup directory. Defaults to "data/backup".
    
    Returns:
        list: Available backups with metadata
    """
    # ...

def restore_from_backup(backup_path, current_db_path="data/drone_search.db"):
    """Restore database from a backup file
    
    Args:
        backup_path (str): Path to backup file
        current_db_path (str, optional): Path to current database.
                                        Defaults to "data/drone_search.db".
    
    Returns:
        bool: True if successful, False otherwise
    """
    # ...
```

## Extended API Documentation

For complete API documentation including all methods, parameters, and return values, please refer to the source code and docstrings. The application follows Google-style docstrings for comprehensive documentation.
