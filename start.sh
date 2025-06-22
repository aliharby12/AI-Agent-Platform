#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
timeout=30
counter=0
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
  counter=$((counter + 1))
  if [ $counter -eq $timeout ]; then
    echo "Database connection timeout"
    exit 1
  fi
done
echo "Database is ready!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000