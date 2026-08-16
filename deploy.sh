#!/bin/bash
set -e

echo "Starting TaskFlow Deployment Process..."

# 1. Update source code
echo "Pulling latest changes from repository..."
git pull origin main

# 2. Build the Docker images
echo "Building Docker images..."
docker-compose build

# 3. Start the application stack (detached mode)
echo "Starting application stack (PostgreSQL, Redis, FastAPI, Celery)..."
docker-compose up -d

# 4. Wait for database to be ready (rudimentary check)
echo "Waiting for PostgreSQL to be ready..."
sleep 5

# 5. Run database migrations
echo "Running Alembic migrations..."
docker-compose exec -T api alembic upgrade head

echo "Deployment complete! TaskFlow is now running."
echo "API: http://localhost:8000"
echo "Check logs with: docker-compose logs -f"
