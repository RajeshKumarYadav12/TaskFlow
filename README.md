# TaskFlow API

TaskFlow is a small Task Management API built with FastAPI, PostgreSQL, Redis, and Celery, implementing a clean MVC architectural pattern.

## Architecture

- **Web Framework**: FastAPI (Python 3.11+) for high performance and automatic interactive API documentation.
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic for migrations.
- **Caching & Broker**: Redis is used both to cache `GET /tasks` responses and as the message broker for Celery.
- **Background Jobs**: Celery handles notifications (e.g. task reassignment and periodic overdue checks).
- **Authentication**: JWT (JSON Web Tokens) with hashed passwords using bcrypt.

## Setup Instructions (Local using Docker)

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd TaskFlow
   ```

2. **Start the stack**:
   This single command brings up the database, redis, background worker, and web app.
   ```bash
   docker-compose up --build
   ```

3. **Access the API**:
   - The API will be available at `http://localhost:8000`
   - Interactive Swagger docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`
   - Metrics: `http://localhost:8000/metrics`

## Running Tests

To run tests locally, install the requirements and run `pytest`:
```bash
pip install -r requirements.txt
pytest
```
*Note: The test suite uses an in-memory SQLite database and a fake redis client so you do not need the real services running to run the API tests.*

## Deployment Path (Render)

This project can be easily deployed to [Render.com](https://render.com) using a Docker-based approach.

1. **Database and Redis**:
   - Create a new PostgreSQL instance on Render.
   - Create a new Redis instance on Render.
   - Copy their internal connection URLs.

2. **Web Service (FastAPI)**:
   - Create a new "Web Service" in Render, connecting this GitHub repository.
   - Environment: Docker.
   - Build Command: Render automatically builds the `Dockerfile`.
   - Start Command: Handled by `CMD` in Dockerfile, or override to `sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"`.
   - Set environment variables: `DATABASE_URL`, `REDIS_URL`, `CELERY_BROKER_URL` (use Redis URL), `CELERY_RESULT_BACKEND` (use Redis URL), and `SECRET_KEY`.

3. **Background Worker (Celery)**:
   - Create a new "Background Worker" in Render, connecting the same repo.
   - Environment: Docker.
   - Start Command: `celery -A app.worker.celery_app worker --loglevel=info`.
   - Copy the same environment variables over.

## Tradeoffs & What I'd do with more time

1. **Cache Invalidation**: Currently, I delete all cached responses for a specific user whenever they create, update, or delete a task (`keys tasks:{user_id}:*`). This is a blunt instrument. With more time, I would implement more granular invalidation or use a cache tagging strategy to only invalidate the exact queries that changed. Using `KEYS` in Redis is also a bad practice in production; I would use `SCAN` or maintain a Redis Set of active keys for each user.
2. **Notification Delivery**: The notification logic is heavily simplified. Notifications are just dumped into a database table. In reality, I would integrate SendGrid (email) or Twilio (SMS), implement a retry policy for failed deliveries in Celery, and add user notification preferences.
3. **Database Migrations in Docker**: In the `docker-compose.yml`, the web server attempts to run `alembic upgrade head` before starting `uvicorn`. In a real production system with multiple replicas, this can cause race conditions. Migrations should ideally run in an init container or a separate release phase pipeline step.
4. **Pagination**: Limit/Offset pagination becomes slow for large datasets. Keyset (cursor) pagination would be better for scaling the `/tasks` endpoint.
5. **Periodic Celery Beat**: While I created a task to check overdue tasks, I haven't configured a `celery beat` service in docker-compose. In production, I would add a `beat` service that runs `check_overdue_tasks` every hour.
