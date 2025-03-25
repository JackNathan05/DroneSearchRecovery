# Application Architecture

This document outlines the architecture of the Drone Search & Recovery application.

## Overview

The application follows a modular architecture with clear separation of concerns. The primary architectural patterns used are:

1. **Model-View-Controller (MVC)** - Separation of data, presentation, and control logic
2. **Repository Pattern** - Abstraction of data storage and retrieval
3. **Service-Oriented Architecture** - Modular components with well-defined interfaces

## Component Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  UI Components  │◄───►│  Controllers    │◄───►│  Services       │
│  (Views)        │     │                 │     │                 │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Repositories   │◄───►│  ORM Models     │◄───►│  Database       │
│                 │     │                 │     │                 │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Key Components

### 1. Views (UI Components)

The UI is built using PyQt6 and organized into several main components:

- **MainWindow** - The application container with navigation sidebar
- **LoginWidget** - User authentication screen
- **MissionPlannerWidget** - Mission creation and configuration
- **MissionViewWidget** - Active mission display with map and chat

Views are instantiated by the main window and interact with the application through signals and slots.

### 2. Data Models

Data models use SQLAlchemy ORM to map between Python objects and database tables:

- **User** - Authentication and user information
- **Mission** - Mission metadata and configuration
- **MissionBoundary** - Geographic boundaries for search areas
- **ChatMessage** - User-system interaction history
- **FlightPlan** - Drone flight parameters and paths
- **WeatherData** - Environmental conditions for missions

Models include relationships, validation, and serialization/deserialization capabilities.

### 3. Repositories

Repositories abstract data access operations:

- **BaseRepository** - Core CRUD operations
- **UserRepository** - User authentication and management
- **MissionRepository** - Mission operations and relationships

Each repository handles transaction management, error recovery, and provides a clean API for data operations.

### 4. Utilities

Helper modules that provide common functionality:

- **Config** - Application configuration management
- **BackupManager** - Database backup and recovery
- **Logger** - Centralized logging

### 5. Database

A SQLite database used for persistent storage with:

- Automatic schema creation
- Transaction support
- Backup and recovery mechanisms

## Control Flow

1. The application starts in `main.py`
2. The database is initialized and default users created
3. The main window is instantiated and displayed
4. The user logs in through the login screen
5. After authentication, missions are loaded from the database
6. User interactions trigger operations through repositories
7. Data changes are persisted to the database

## Design Patterns

Several design patterns are employed throughout the application:

1. **Repository Pattern** - Abstracts data access operations
2. **Singleton** - For configuration and database connection
3. **Observer** (via Qt Signals/Slots) - For UI event handling
4. **Command** - For undoable operations
5. **Factory** - For creating complex objects

## Dependencies Between Modules

- **Views** depend on **Controllers** but not on **Repositories**
- **Repositories** depend on **Models** but not on **Views**
- **Models** have no dependencies on other application components
- **Utilities** are independent and used by all other components

## Future Extensibility

The modular architecture allows for:

1. Replacing the UI framework without affecting business logic
2. Switching database backends by updating the Repository implementations
3. Adding new mission types through the existing interfaces
4. Expanding functionality with additional modules while maintaining separation of concerns
