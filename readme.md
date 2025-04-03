# Drone Search & Recovery Application

A sophisticated desktop application for controlling drones to conduct search and recovery operations using natural language processing and AI for object detection.

## Features

- Natural language control for specifying search locations
- Interactive mapping interface with multiple view options
- Automated flight planning based on search parameters
- Weather integration for optimal flight conditions
- Real-time video processing with AI object detection
- Detailed search results and reporting
- Multi-user support with role-based access control

## Current Status

Phase 1 and Phase 2 have been completed, including:
- Core UI framework and navigation
- User authentication system
- Database integration with SQLAlchemy ORM
- Mission management and storage
- Backup and recovery systems
- Advanced mapping functionality with Folium integration
- Drawing tools for defining search areas
- Drone connection and command interface with DroneKit
- Drone state monitoring and telemetry
- Comprehensive flight planning with configurable parameters
- Flight path optimization with elevation data consideration
- Terrain contouring capabilities for both grid and spiral search patterns
- Camera angle optimization with real-time coverage visualization

## Installation

### Requirements

- Python 3.10 or higher
- Windows 10/11 64-bit (primary platform)
- SQLite

### Dependencies

```bash
# Core libraries
PyQt6              # UI framework
folium             # Map integration
geopy              # Geographic utilities
dronekit           # Drone communication
pymavlink          # MAVLink protocol support
sqlalchemy         # Database ORM
pandas             # Data handling
shapely            # Geometric operations
matplotlib         # Visualization
pytest             # Testing framework
```

### Setup Instructions

1. Clone the repository
```bash
git clone https://github.com/yourusername/DroneSearchRecovery.git
cd DroneSearchRecovery
```

2. Create a virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the application
```bash
python src/main.py
```

## Default Users

The application creates the following default users on first run:
- Username: `admin`, Password: `admin123` (Administrator account)
- Username: `1`, Password: `1` (Test user account)

## Project Structure

```
DroneSearchRecovery/
├── src/                    # Source code
│   ├── controllers/        # Business logic
│   ├── drone/              # Drone communication and control
│   ├── mapping/            # Map generation and management
│   ├── planning/           # Flight planning algorithms
│   ├── models/             # Data models
│   ├── repositories/       # Data access layer
│   ├── views/              # UI components
│   ├── utils/              # Helper functions
│   ├── tests/              # Test suite
│   ├── resources/          # Images, icons, etc.
├── data/                   # Data storage
│   ├── missions/           # Mission data
│   ├── maps/               # Generated maps
│   ├── logs/               # Application logs
│   └── backup/             # Backup files
├── docs/                   # Documentation
│   ├── design/             # Design documents
│   ├── api/                # API documentation
│   └── user/               # User manual
├── venv/                   # Virtual environment (gitignored)
```

## Key Features Implemented

### User Authentication
- Local user authentication system
- Role-based permissions
- Password hashing for security

### Mission Management
- Create, view, and manage missions
- Mission history tracking
- Chat interface for mission planning

### Mapping Interface
- Interactive maps with Folium
- Satellite and topographic views
- Drawing tools for defining search areas
- Flight path visualization

### Flight Planning
- Grid search pattern generation
- Spiral search pattern generation
- Terrain contouring for both search patterns
- Elevation data consideration for path optimization
- Automated waypoint creation and optimization
- Adjustable camera angles with live coverage visualization
- Customizable flight parameters (altitude, speed, overlap)

### Drone Control
- Connection to physical or simulated drones
- Command transmission (arm, takeoff, land, etc.)
- Real-time state monitoring
- Mission upload and download

### Database and Storage
- SQLAlchemy ORM for database access
- Automated backup system
- Data import/export capabilities

## System Requirements

### Minimum Requirements
- Windows 10 64-bit
- Intel Core i5 (8th gen) or equivalent
- 8GB RAM
- 20GB free storage
- Basic GPU capabilities

### Recommended Requirements
- Windows 10/11 64-bit
- Intel Core i7 (10th gen) or better
- 16GB+ RAM
- 50GB+ SSD storage
- NVIDIA GPU with CUDA support (for future AI detection)
