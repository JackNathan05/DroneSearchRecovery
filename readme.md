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

## Status

Phase 1 of development is complete, including:
- Core UI framework and navigation
- User authentication system
- Database integration and persistence
- Mission management 
- Backup and recovery systems

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
transformers       # NLP capabilities
opencv-python      # Computer vision
dronekit           # Drone communication
pymavlink          # MAVLink protocol support
sqlalchemy         # Database ORM
pandas             # Data handling
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
│   ├── models/             # Data models
│   ├── views/              # UI components
│   ├── utils/              # Helper functions
│   ├── repositories/       # Data access layer
│   ├── resources/          # Images, icons, etc.
│   ├── tests/              # Test suite
│   ├── __init__.py         # Package marker
│   └── main.py             # Application entry point
├── data/                   # Data storage
│   ├── missions/           # Mission data
│   ├── logs/               # Application logs
│   └── backup/             # Backup files
├── docs/                   # Documentation
│   ├── design/             # Design documents
│   ├── api/                # API documentation
│   └── user/               # User manual
├── venv/                   # Virtual environment (gitignored)
├── requirements.txt        # Dependencies
├── README.md               # This file
├── CHANGELOG.md            # Version history
└── LICENSE                 # License information
```

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
- NVIDIA GPU with CUDA support
