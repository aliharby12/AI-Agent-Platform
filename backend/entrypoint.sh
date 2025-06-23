#!/bin/bash
set -e

cd /backend

echo "Starting FastAPI application..."

# Function to wait for PostgreSQL
wait_for_postgres() {
    echo "Waiting for PostgreSQL to be ready..."
    while ! pg_isready -h db -p 5432 -U fastapi_user; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 2
    done
    echo "PostgreSQL is up and running!"
}

# Function to run migrations
run_migrations() {
    echo "Running database migrations..."
    alembic upgrade head
    echo "Migrations completed successfully!"
}

# Function to initialize alembic if needed
initialize_alembic() {
    if [ ! -d "alembic" ]; then
        echo "Initializing Alembic..."
        alembic init alembic
        
        # Replace the env.py with our custom version
        cat > alembic/env.py << 'EOF'
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Import your models here
from models import Base

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option(
    "sqlalchemy.url", 
    os.getenv("DATABASE_URL", "postgresql://fastapi_user:fastapi_password@localhost:5432/fastapi_db")
)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOF
        
        echo "Creating initial migration..."
        alembic revision --autogenerate -m "Initial migration"
    fi
}

# Main execution flow
wait_for_postgres
initialize_alembic
run_migrations

# Start the FastAPI application
echo "Starting FastAPI server..."
exec "$@"