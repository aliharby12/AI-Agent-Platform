import os
import sys
import time
import subprocess
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

def wait_for_database(max_retries=30, delay=2):
    """Wait for database to be available"""
    print("Waiting for database connection...")
    
    for attempt in range(max_retries):
        try:
            DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:your_secure_password_here@localhost:5432/ai_agent_platform")
            engine = create_engine(DATABASE_URL)
            connection = engine.connect()
            connection.close()
            print("Database is ready!")
            return True
        except OperationalError as e:
            print(f"Database not ready (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(delay)
    
    print("Failed to connect to database after maximum retries")
    return False

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def initialize_alembic():
    """Initialize Alembic if not already initialized"""
    if not os.path.exists("alembic"):
        print("Initializing Alembic...")
        if not run_command("alembic init alembic"):
            return False
        
        # Update env.py with proper configuration
        env_content = '''import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv
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
'''
        
        with open("alembic/env.py", "w") as f:
            f.write(env_content)
        
        print("Creating initial migration...")
        if not run_command('alembic revision --autogenerate -m "Initial migration"'):
            return False
    
    return True

def run_migrations():
    """Run database migrations"""
    print("Running migrations...")
    return run_command("alembic upgrade head")

def main():
    """Main migration process"""
    print("Starting migration process...")
    
    # Wait for database
    if not wait_for_database():
        sys.exit(1)
    
    # Initialize Alembic if needed
    if not initialize_alembic():
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        sys.exit(1)
    
    print("Migration process completed successfully!")

if __name__ == "__main__":
    main()