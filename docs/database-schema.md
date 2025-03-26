# Database Schema Documentation

This document describes the database schema for the Drone Search & Recovery application.

## Overview

The application uses SQLAlchemy ORM with a SQLite backend. The schema is designed to support:

- User authentication and management
- Mission creation and storage
- Geographic boundary definitions
- Chat/command history
- Flight planning
- Weather data integration

## Entity-Relationship Diagram

```
┌─────────────┐       ┌───────────────┐       ┌─────────────────┐
│             │       │               │       │                 │
│   User      │──1:N──│   Mission     │──1:N──│  MissionBoundary│
│             │       │               │       │                 │
└─────────────┘       └───────────────┘       └─────────────────┘
                           │  │  │
                           │  │  │
                 ┌─────────┘  │  └─────────┐
                 │            │            │
                 │            │            │
                 ▼            ▼            ▼
        ┌─────────────┐ ┌───────────┐ ┌───────────┐
        │             │ │           │ │           │
        │ ChatMessage │ │FlightPlan │ │WeatherData│
        │             │ │           │ │           │
        └─────────────┘ └───────────┘ └───────────┘
```

## Tables

### Users

Stores user authentication and identification information.

| Column         | Type         | Description                       |
|----------------|--------------|-----------------------------------|
| id             | Integer      | Primary key                       |
| username       | String(50)   | Unique username                   |
| password_hash  | String(128)  | Hashed password with salt         |
| created_at     | DateTime     | Account creation timestamp        |
| last_login     | DateTime     | Last successful login             |
| is_admin       | Boolean      | Administrator privileges flag     |

### Missions

Stores mission metadata and configuration.

| Column         | Type         | Description                       |
|----------------|--------------|-----------------------------------|
| id             | Integer      | Primary key                       |
| name           | String(100)  | Mission name                      |
| user_id        | Integer      | Foreign key to users.id           |
| created_at     | DateTime     | Creation timestamp                |
| updated_at     | DateTime     | Last modification timestamp       |
| status         | String(20)   | Mission status (new, in_progress, etc.) |
| mission_type   | String(20)   | Type of mission (custom, imported) |
| description    | Text         | Mission description               |

### Mission Boundaries

Stores geographic boundaries for search areas.

| Column         | Type         | Description                       |
|----------------|--------------|-----------------------------------|
| id             | Integer      | Primary key                       |
| mission_id     | Integer      | Foreign key to missions.id        |
| boundary_type  | String(20)   | Type of boundary (polygon, circle, etc.) |
| coordinates    | Text         | JSON string of coordinates        |

### Chat Messages

Stores conversation history for missions.

| Column         | Type         | Description                       |
|----------------|--------------|-----------------------------------|
| id             | Integer      | Primary key                       |
| mission_id     | Integer      | Foreign key to missions.id        |
| user_id        | Integer      | Foreign key to users.id (null for system) |
| timestamp      | DateTime     | Message timestamp                 |
| sender_type    | String(10)   | Message source (user, system)     |
| message        | Text         | Message content                   |

### Flight Plans

Stores drone flight paths and parameters.

| Column         | Type         | Description                       |
|----------------|--------------|-----------------------------------|
| id             | Integer      | Primary key                       |
| mission_id     | Integer      | Foreign key to missions.id        |
| created_at     | DateTime     | Creation timestamp                |
| updated_at     | DateTime     | Last modification timestamp       |
| pattern_type   | String(20)   | Search pattern (grid, spiral, etc.) |
| parameters     | Text         | JSON string of flight parameters  |
| status         | String(20)   | Plan status (draft, ready, executed) |
| altitude       | Float        | Flight altitude in meters         |
| speed          | Float        | Flight speed in m/s               |
| overlap        | Float        | Image overlap percentage          |
| camera_angle   | Float        | Camera angle in degrees           |

### Weather Data

Stores weather information for missions.

| Column         | Type         | Description                       |
|----------------|--------------|-----------------------------------|
| id             | Integer      | Primary key                       |
| mission_id     | Integer      | Foreign key to missions.id        |
| timestamp      | DateTime     | Data collection timestamp         |
| data           | Text         | JSON string of weather data       |
| temperature    | Float        | Temperature in Celsius            |
| wind_speed     | Float        | Wind speed in m/s                 |
| wind_direction | Float        | Wind direction in degrees         |
| precipitation  | Float        | Precipitation in mm               |

## Relationships

The schema implements the following relationships:

- **User** → **Missions**: One-to-many (A user can have multiple missions)
- **Mission** → **MissionBoundary**: One-to-many (A mission can have multiple boundaries)
- **Mission** → **ChatMessage**: One-to-many (A mission has a conversation history)
- **Mission** → **FlightPlan**: One-to-many (A mission can have multiple flight plans)
- **Mission** → **WeatherData**: One-to-many (A mission can have multiple weather records)

## Data Serialization

Complex data structures are serialized as JSON strings:

- Mission boundary coordinates
- Flight plan parameters
- Weather data

This approach balances the advantages of structured queries with flexibility for complex data types.

## Indexes

The following indexes improve query performance:

- `username` in Users table (unique)
- `user_id` in Missions table
- `mission_id` in all related tables

## Data Validation

Data validation occurs at three levels:

1. **SQLAlchemy Model Level**: Type constraints, NOT NULL constraints
2. **Repository Level**: Business logic validation
3. **Database Level**: Foreign key constraints, unique constraints

## Backup and Recovery

The database includes automatic backup functionality:

- Time-stamped backup files
- Configurable backup frequency
- Backup rotation to manage storage
- Point-in-time recovery capability