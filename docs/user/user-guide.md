# User Guide

## Introduction

This guide provides instructions for using the Drone Search & Recovery application. The application is designed to help plan and execute drone search operations using natural language commands and automated flight planning.

## Getting Started

### Launching the Application

1. Ensure you have installed the application following the instructions in the README.md file
2. Run the application by executing: `python src/main.py`
3. The login screen will appear

### Login

1. Use one of the following default accounts:
   - Username: `admin`, Password: `admin123` (Administrator account)
   - Username: `1`, Password: `1` (Test user account)
2. Enter your credentials and click "Login"
3. Upon successful login, you will see the home screen with your missions listed in the sidebar

## Navigation

### Main Interface

The application interface consists of several key areas:

- **Sidebar**: On the left side, displaying your account information and list of missions
- **Content Area**: The main display area that changes based on the current screen
- **Navigation Controls**: Buttons for moving between screens

### Sidebar Features

- **Toggle Button**: Click the "≡" button to collapse or expand the sidebar
- **Account Section**: Displays your username
- **Missions Section**: Lists all your missions
- **Logout Button**: Ends your session and returns to the login screen

## Creating Missions

### New Mission

1. From the home screen, click the "New Mission" button
2. Enter a name for your mission in the "What should this mission be called?" field
3. Use the chat interface to describe your search mission in natural language
4. Click "Create Mission" to save the mission

### Import Mission

1. From the home screen, click the "Import Mission" button
2. A new mission will be created with default settings
3. You can then modify it according to your needs

## Managing Missions

### Opening a Mission

- Click on any mission name in the sidebar to open it
- The active mission is highlighted with a darker color

### Renaming a Mission

1. Right-click on a mission in the sidebar
2. Select "Rename Mission" from the context menu
3. Enter the new name and click "OK"

### Deleting a Mission

1. Right-click on a mission in the sidebar
2. Select "Delete Mission" from the context menu
3. Confirm deletion when prompted

## Working with Missions

### Chat Interface

Each mission includes a chat interface for natural language interaction:

1. Type your command or question in the input field at the bottom
2. Click "Send" or press Enter
3. The system will respond with relevant information or actions

### Mission Data

The mission view shows:

- Chat history on the left side
- Map display on the right side (will be implemented in future phases)
- Flight plan information (will be implemented in future phases)

### Navigation Within Missions

- Click the "← Home" button to return to the home screen
- Use the chat interface to adjust mission parameters

## Backup and Recovery

### Automatic Backups

The application automatically creates backups:

1. When the application starts
2. Every 24 hours while running
3. Before critical operations

### Backup Location

Backups are stored in the `data/backup/` directory with timestamped filenames:
- Format: `drone_search_YYYYMMDD_HHMMSS.db`

### Restoring from Backup

To restore from a backup:

1. Close the application
2. Locate the desired backup file in the `data/backup/` directory
3. Copy it to `data/drone_search.db` (replacing the existing file)
4. Restart the application

## Troubleshooting

### Login Issues

If you cannot log in:
- Verify you are using the correct username and password
- Check that the application has the necessary permissions to access the database

### Missing Missions

If missions are not appearing:
- Check that you are logged in with the correct account
- Verify the database file exists and is not corrupted

### Application Errors

If the application crashes or displays error messages:
- Check the log file in `data/logs/app.log` for detailed information
- Ensure all dependencies are correctly installed
- Try restoring from a backup if the database is corrupted

## Future Features

The following features will be available in upcoming releases:

- Interactive mapping interface
- Flight planning with different search patterns
- Real-time drone control
- AI-powered object detection
- Weather integration
- Multi-user collaboration

Please refer to the project roadmap for development timelines.
