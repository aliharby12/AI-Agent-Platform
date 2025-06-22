# AI-Agent-Platform

Backend service for an AI Agent Platform, enabling users to create, manage, and interact with AI agents via text and voice.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start (Docker)](#quick-start-docker)
- [Manual Setup](#manual-setup)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)

## Prerequisites

Before running this project, ensure you have the following installed:

- **Docker and Docker Compose** (recommended for easy setup)
  - Docker Engine 20.10+
  - Docker Compose 2.0+
- **Python 3.11+** (for manual setup)
- **PostgreSQL 15+** (for manual setup)
- **OpenAI API Key** (required for AI functionality)

## Quick Start (Docker)

This is the easiest way to get the project running:

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd AI-Agent-Platform
```

### Step 2: Set Up Environment Variables
```bash
# Copy the example environment file
cp .env-example .env

# Edit the .env file with your configuration
nano .env
```

**Required environment variables:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `JWT_SECRET_KEY`: A secure random string for JWT tokens
- `DB_PASSWORD`: A secure password for the PostgreSQL database
- `SECRET_KEY`: A secure random string for the application

### Step 3: Build and Run with Docker Compose
```bash
# Build and start all services
sudo docker-compose up --build

# Or run in detached mode
sudo docker-compose up --build -d
```

### Step 4: Verify the Application
- API will be available at: http://localhost:8000
- API documentation at: http://localhost:8000/docs
- Database will be accessible at localhost:5432

## Manual Setup

If you prefer to run the application without Docker:

### Step 1: Set Up Python Environment
```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Set Up PostgreSQL Database
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE ai_agent_platform;
CREATE USER ai_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ai_agent_platform TO ai_user;
\q
```

### Step 3: Configure Environment
```bash
# Copy and edit environment file
cp .env-example .env
nano .env
```

Update the following variables for manual setup:
```env
DATABASE_URL=postgresql+asyncpg://ai_user:your_secure_password@localhost:5432/ai_agent_platform
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_agent_platform
DB_USER=ai_user
DB_PASSWORD=your_secure_password
```

### Step 4: Run the Application
```bash
# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Environment Configuration

The application uses the following environment variables:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI functionality | Yes | - |
| `JWT_SECRET_KEY` | Secret key for JWT token generation | Yes | - |
| `JWT_ALGORITHM` | JWT algorithm | No | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token expiry | No | 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | JWT refresh token expiry | No | 7 |
| `DATABASE_URL` | Database connection string | Yes | - |
| `DB_HOST` | Database host | Yes | db (Docker) / localhost |
| `DB_PORT` | Database port | No | 5432 |
| `DB_NAME` | Database name | No | ai_agent_platform |
| `DB_USER` | Database user | No | postgres |
| `DB_PASSWORD` | Database password | Yes | - |
| `DEBUG` | Debug mode | No | False |
| `SECRET_KEY` | Application secret key | Yes | - |
| `ENVIRONMENT` | Environment name | No | production |

## Running the Application

### Using Docker Compose
```bash
# Start all services
sudo docker-compose up --build

# Start in detached mode
sudo docker-compose up --build -d

# View logs
sudo docker-compose logs -f

# Stop all services
sudo docker-compose down

# Stop and remove volumes
sudo docker-compose down -v
```

### Using Python Directly
```bash
# Activate virtual environment
source venv/bin/activate

# Run with auto-reload (development)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run in production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Testing

### Run All Tests
```bash
# Using Docker
sudo docker-compose exec ai-agent-platform pytest -v ./tests

# Using Python directly
pytest -v ./tests
```

### Run Specific Test Files
```bash
# Test authentication
sudo docker-compose exec ai-agent-platform pytest -v ./tests/test_auth.py

# Test agents
sudo docker-compose exec ai-agent-platform pytest -v ./tests/test_agents.py

# Test sessions
sudo docker-compose exec ai-agent-platform pytest -v ./tests/test_sessions.py
```

### Run Specific Test Functions
```bash
# Test voice message functionality
sudo docker-compose exec ai-agent-platform pytest -v ./tests/test_sessions.py::test_voice_message

# Test agent creation
sudo docker-compose exec ai-agent-platform pytest -v ./tests/test_agents.py::test_create_agent
```

## API Documentation

Once the application is running, you can access:

- **Interactive API Documentation**: http://localhost:8000/docs
- **Alternative API Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Project Structure

```
AI-Agent-Platform/
├── app/                    # Main application code
│   ├── api/               # API routes and schemas
│   │   ├── routers/       # Route handlers
│   │   └── schemas/       # Pydantic models
│   ├── models/            # Database models
│   ├── services/          # Business logic services
│   ├── utils/             # Utility functions
│   └── main.py           # FastAPI application entry point
├── data/                  # PostgreSQL data (Docker)
├── static/                # Static files (audio, etc.)
├── uploads/               # User uploaded files
├── tests/                 # Test files
├── docker-compose.yml     # Docker services configuration
├── Dockerfile            # Docker image definition
├── requirements.txt      # Python dependencies
└── .env-example         # Environment variables template
```

## Troubleshooting

### Common Issues

1. **Port 8000 already in use**
   ```bash
   # Find and kill the process
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

2. **Database connection issues**
   ```bash
   # Check if PostgreSQL is running
   sudo systemctl status postgresql
   
   # Restart PostgreSQL
   sudo systemctl restart postgresql
   ```

3. **Docker permission issues**
   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   # Log out and back in, or run:
   newgrp docker
   ```

4. **Environment variables not loaded**
   ```bash
   # Ensure .env file exists and has correct format
   cp .env-example .env
   # Edit .env file with your values
   ```

### Getting Help

- Check the logs: `sudo docker-compose logs -f`
- Verify environment variables are set correctly
- Ensure all prerequisites are installed
- Check API documentation at http://localhost:8000/docs