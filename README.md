# AI-Agent-Platform

Backend service for an AI Agent Platform, enabling users to create, manage, and interact with AI agents via text and voice.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start (Docker)](#quick-start-docker)
- [Manual Setup](#manual-setup)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Ensure you have the following installed:

- **Docker & Docker Compose** (recommended)
      - Docker Engine 20.10+
      - Docker Compose 2.0+
- **Python 3.11+** (for manual setup)
- **PostgreSQL 15+** (for manual setup)
- **OpenAI API Key** (for AI features)

---

## Quick Start (Docker)

The easiest way to run the project is with Docker Compose and Nginx as a reverse proxy.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI-Agent-Platform
```

### 2. Configure Environment Variables

```bash
cp .env-example .env
nano .env
```

### 3. Build & Run (with Nginx and scaling)

```bash
# Run with Nginx as the main entry point (port 80)
sudo docker-compose up --build --scale backend=3 --scale frontend=1
# Or detached:
sudo docker-compose up --build -d --scale backend=3 --scale frontend=1
```

- You can adjust the number of backend/frontend containers as needed.
- Nginx will load balance API requests to all backend containers.

### 4. Access Services

- **Main entry point (Nginx):** [http://localhost](http://localhost)
    - **Backend API:** [http://localhost/api/](http://localhost/api/)
    - **Frontend:** [http://localhost](http://localhost)
- **Database:** `localhost:5432`

> **Note:** Do not access the backend directly on port 8000; use Nginx on port 80 for all API and frontend requests.

---

## Manual Setup

Prefer not to use Docker? Follow these steps:

### 1. Python Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 2. PostgreSQL Setup

```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

sudo -u postgres psql
# In psql shell:
CREATE DATABASE ai_agent_platform;
CREATE USER ai_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ai_agent_platform TO ai_user;
\q
```

### 3. Environment Variables

```bash
cp .env-example .env
nano .env
```

Update:

```env
DATABASE_URL=postgresql+asyncpg://ai_user:your_secure_password@localhost:5432/ai_agent_platform
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_agent_platform
DB_USER=ai_user
DB_PASSWORD=your_secure_password
```

### 4. Run the Application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Environment Configuration

| Variable                     | Description                        | Required | Default                    |
|------------------------------|------------------------------------|----------|----------------------------|
| `OPENAI_API_KEY`             | OpenAI API key                     | Yes      | -                          |
| `JWT_SECRET_KEY`             | JWT secret key                     | Yes      | -                          |
| `JWT_ALGORITHM`              | JWT algorithm                      | No       | HS256                      |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| JWT access token expiry (minutes)  | No       | 30                         |
| `REFRESH_TOKEN_EXPIRE_DAYS`  | JWT refresh token expiry (days)    | No       | 7                          |
| `DB_HOST`                    | Database host                      | Yes      | db (Docker) / localhost    |
| `DB_PORT`                    | Database port                      | No       | 5432                       |
| `DB_NAME`                    | Database name                      | No       | ai_agent_platform          |
| `DB_USER`                    | Database user                      | No       | postgres                   |
| `DB_PASSWORD`                | Database password                  | Yes      | -                          |
| `DEBUG`                      | Debug mode                         | No       | False                      |
| `SECRET_KEY`                 | Application secret key             | Yes      | -                          |
| `ENVIRONMENT`                | Environment name                   | No       | production                 |

---

## Running the Application

### With Docker Compose (Nginx as entry point)

```bash
sudo docker-compose up --build --scale backend=3 --scale frontend=1
# Detached:
sudo docker-compose up --build -d --scale backend=3 --scale frontend=1
# Logs:
sudo docker-compose logs -f
# Stop:
sudo docker-compose down
# Remove volumes:
sudo docker-compose down -v
```

- Access everything via [http://localhost](http://localhost)
- Nginx will route `/api/` to the backend and all other requests to the frontend.

### With Python

```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload  # Dev
uvicorn app.main:app --host 0.0.0.0 --port 8000           # Prod
```

---

## Testing

```bash
# Docker:
sudo docker-compose run --rm test

# Python:
pytest -v ./tests
```

---

## API Documentation

- **Swagger UI:** [http://localhost/api/docs](http://localhost/api/docs)
- **ReDoc:** [http://localhost/api/redoc](http://localhost/api/redoc)
- **OpenAPI Schema:** [http://localhost/api/openapi.json](http://localhost/api/openapi.json)

---

## Troubleshooting

### Common Issues

1. **Port 80 in use**
      ```bash
      sudo lsof -i :80
      sudo kill -9 <PID>
      ```

2. **Database connection**
      ```bash
      sudo systemctl status postgresql
      sudo systemctl restart postgresql
      ```

3. **Docker permissions**
      ```bash
      sudo usermod -aG docker $USER
      newgrp docker
      ```

4. **Environment variables not loaded**
      ```bash
      cp .env-example .env
      # Edit .env with your values
      ```

### Need Help?

- Check logs: `sudo docker-compose logs -f`
- Verify environment variables
- Ensure prerequisites are installed
- Review API docs: [http://localhost/api/docs](http://localhost/api/docs)

---

