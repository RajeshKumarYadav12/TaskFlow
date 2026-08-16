<div align="center">

# TaskFlow API

**Task Management REST API built with FastAPI, PostgreSQL, Redis, Celery, JWT Authentication and Docker**

A backend service for managing users, projects, tasks and notifications with caching, background processing, database migrations and monitoring.

</div>

## Overview

TaskFlow follows a clean MVC architecture and provides authentication, project management, task management, filtering, Redis caching, asynchronous notifications and operational monitoring.

## Quick Start

```bash
git clone <repo-url>
cd TaskFlow
docker-compose up --build
```

Open Swagger:

```text
http://localhost:8000/docs
```

Check application health:

```text
http://localhost:8000/health
```

View metrics:

```text
http://localhost:8000/metrics
```

## Tech Stack

| Component        | Technology        |
| ---------------- | ----------------- |
| Backend          | FastAPI           |
| Language         | Python 3.11+      |
| Database         | PostgreSQL        |
| ORM              | SQLAlchemy        |
| Migrations       | Alembic           |
| Cache / Broker   | Redis             |
| Background Jobs  | Celery            |
| Authentication   | JWT               |
| Password Hashing | bcrypt            |
| Containerization | Docker            |
| Testing          | Pytest            |
| Deployment       | Render            |
| API Docs         | Swagger / OpenAPI |

## Features

| Feature        | Description                           |
| -------------- | ------------------------------------- |
| Authentication | Signup, login and logout              |
| Authorization  | JWT Bearer token authentication       |
| Projects       | Complete project CRUD                 |
| Tasks          | Complete task CRUD                    |
| Filtering      | Status, assignee and due date filters |
| Pagination     | Skip and limit support                |
| Caching        | Redis caching for task listing        |
| Notifications  | Celery based background notifications |
| Health Check   | PostgreSQL and Redis status           |
| Metrics        | Requests, errors and response time    |
| Migrations     | Alembic database migrations           |
| Docker         | Complete local development stack      |

## Architecture

```text
                         Client
                           │
                           ▼
                    ┌─────────────┐
                    │   FastAPI   │
                    │ REST API    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           Auth        Projects       Tasks
              │            │            │
              └────────────┼────────────┘
                           ▼
                    Service Layer
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
            PostgreSQL             Redis
             Database          Cache / Broker
                                    │
                                    ▼
                                  Celery
                              Background Jobs
```

## Request Flow

```text
Client
  │
  ▼
FastAPI Router
  │
  ▼
JWT Authentication
  │
  ▼
Request Validation
  │
  ▼
Service Layer
  │
  ├──► Redis Cache
  │
  └──► PostgreSQL
         │
         ▼
      Response
```

Task notification flow:

```text
Update Task
    │
    ▼
PostgreSQL
    │
    ▼
Celery Task
    │
    ▼
Notification
    │
    ▼
Notification Table
```

## Project Structure

```text
TaskFlow/
├── app/
│   ├── main.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   ├── repositories/
│   ├── core/
│   ├── db/
│   └── worker/
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
└── README.md
```

## Authentication

TaskFlow uses JWT access tokens with bcrypt password hashing.

```text
Signup
  ↓
Hash Password
  ↓
Store User
  ↓
Login
  ↓
Generate JWT
  ↓
Authorization: Bearer <token>
```

Protected endpoints require:

```http
Authorization: Bearer <your_access_token>
```

## API Reference

### Authentication

| No. | Method | Endpoint              | Auth   | Description           |
| --: | ------ | --------------------- | ------ | --------------------- |
|   1 | POST   | `/api/v1/auth/signup` | Public | Register user         |
|   2 | POST   | `/api/v1/auth/login`  | Public | Login and receive JWT |
|   3 | POST   | `/api/v1/auth/logout` | Bearer | Logout user           |

### Projects

| No. | Method | Endpoint                        | Auth   | Description       |
| --: | ------ | ------------------------------- | ------ | ----------------- |
|   4 | POST   | `/api/v1/projects/`             | Bearer | Create project    |
|   5 | GET    | `/api/v1/projects/`             | Bearer | Get user projects |
|   6 | GET    | `/api/v1/projects/{project_id}` | Bearer | Get project       |
|   7 | PUT    | `/api/v1/projects/{project_id}` | Bearer | Update project    |
|   8 | DELETE | `/api/v1/projects/{project_id}` | Bearer | Delete project    |

### Tasks

| No. | Method | Endpoint                  | Auth   | Description          |
| --: | ------ | ------------------------- | ------ | -------------------- |
|   9 | POST   | `/api/v1/tasks/`          | Bearer | Create task          |
|  10 | GET    | `/api/v1/tasks/`          | Bearer | Get and filter tasks |
|  11 | GET    | `/api/v1/tasks/{task_id}` | Bearer | Get task             |
|  12 | PUT    | `/api/v1/tasks/{task_id}` | Bearer | Update task          |
|  13 | DELETE | `/api/v1/tasks/{task_id}` | Bearer | Delete task          |

### Notifications

| No. | Method | Endpoint                 | Auth   | Description       |
| --: | ------ | ------------------------ | ------ | ----------------- |
|  14 | GET    | `/api/v1/notifications/` | Bearer | Get notifications |

### Operational

| No. | Method | Endpoint   | Auth   | Description             |
| --: | ------ | ---------- | ------ | ----------------------- |
|  15 | GET    | `/health`  | Public | Check API, DB and Redis |
|  16 | GET    | `/metrics` | Public | API statistics          |

## API Examples

### 1. Signup

```http
POST /api/v1/auth/signup
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "password": "mysecurepassword"
}
```

### 2. Login

```http
POST /api/v1/auth/login
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "password": "mysecurepassword"
}
```

Response:

```json
{
  "message": "User login successfully!",
  "status": "success",
  "code": 200,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "token_type": "bearer"
  }
}
```

### 3. Logout

```http
POST /api/v1/auth/logout
Authorization: Bearer <your_access_token>
```

### 4. Create Project

```http
POST /api/v1/projects/
Authorization: Bearer <your_access_token>
```

```json
{
  "name": "Project Alpha",
  "description": "Optional project description"
}
```

### 5. Get Projects

```http
GET /api/v1/projects/?skip=0&limit=100
Authorization: Bearer <your_access_token>
```

### 6. Get Project

```http
GET /api/v1/projects/{project_id}
Authorization: Bearer <your_access_token>
```

### 7. Update Project

```http
PUT /api/v1/projects/{project_id}
Authorization: Bearer <your_access_token>
```

```json
{
  "name": "Updated Project Name"
}
```

### 8. Delete Project

```http
DELETE /api/v1/projects/{project_id}
Authorization: Bearer <your_access_token>
```

### 9. Create Task

```http
POST /api/v1/tasks/
Authorization: Bearer <your_access_token>
```

```json
{
  "title": "Design Homepage",
  "description": "Optional description",
  "project_id": 1,
  "due_date": "2026-08-20T12:00:00Z"
}
```

### 10. Get Tasks

```http
GET /api/v1/tasks/
Authorization: Bearer <your_access_token>
```

Supported filters:

| Parameter        | Description                   |
| ---------------- | ----------------------------- |
| `status`         | `todo`, `in_progress`, `done` |
| `assignee`       | Exact assignee name           |
| `due_date_start` | Minimum due date              |
| `due_date_end`   | Maximum due date              |
| `skip`           | Pagination offset             |
| `limit`          | Maximum results               |

Example:

```http
GET /api/v1/tasks/?status=in_progress&assignee=John%20Doe&skip=0&limit=20
```

Task listing uses Redis caching.

### 11. Get Task

```http
GET /api/v1/tasks/{task_id}
Authorization: Bearer <your_access_token>
```

### 12. Update Task

```http
PUT /api/v1/tasks/{task_id}
Authorization: Bearer <your_access_token>
```

```json
{
  "status": "in_progress",
  "assignee": "John Doe"
}
```

Changing the assignee triggers a background Celery notification.

### 13. Delete Task

```http
DELETE /api/v1/tasks/{task_id}
Authorization: Bearer <your_access_token>
```

### 14. Get Notifications

```http
GET /api/v1/notifications/
Authorization: Bearer <your_access_token>
```

Example:

```json
{
  "message": "Notifications retrieved successfully!",
  "status": "success",
  "code": 200,
  "data": [
    {
      "id": 1,
      "task_id": 4,
      "message": "Task reassigned to John Doe",
      "created_at": "2026-08-15T20:56:55.919222Z"
    }
  ]
}
```

### 15. Health Check

```http
GET /health
```

```json
{
  "status": "ok",
  "database": "connected",
  "redis": "connected"
}
```

### 16. Metrics

```http
GET /metrics
```

```json
{
  "total_requests": 42,
  "total_errors": 2,
  "avg_response_time_seconds": 0.104
}
```

## Standard Response

```json
{
  "message": "Operation completed successfully!",
  "status": "success",
  "code": 200,
  "data": {}
}
```

| Field     | Description           |
| --------- | --------------------- |
| `message` | Human readable result |
| `status`  | Request status        |
| `code`    | HTTP status code      |
| `data`    | Response payload      |

## Local Setup

### Prerequisites

```text
Python 3.11+
Docker
Docker Compose
Git
```

### Clone

```bash
git clone <repo-url>
cd TaskFlow
```

### Start Stack

```bash
docker-compose up --build
```

This starts FastAPI, PostgreSQL, Redis and Celery.

### Access

| Service | URL                                  |
| ------- | ------------------------------------ |
| API     | `http://localhost:8000`              |
| Swagger | `http://localhost:8000/docs`         |
| ReDoc   | `http://localhost:8000/redoc`        |
| OpenAPI | `http://localhost:8000/openapi.json` |
| Health  | `http://localhost:8000/health`       |
| Metrics | `http://localhost:8000/metrics`      |

## Environment Variables

```env
DATABASE_URL=postgresql://user:password@localhost:5432/taskflow
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
SECRET_KEY=your-secret-key
```

Never commit production credentials or secrets.

## Database Migrations

Create migration:

```bash
alembic revision --autogenerate -m "describe migration"
```

Apply migration:

```bash
alembic upgrade head
```

Rollback:

```bash
alembic downgrade -1
```

## Testing

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest
```

The test suite uses an in-memory SQLite database and a fake Redis client, so the real services are not required for API tests.

## Redis Caching

Task listing responses are cached to reduce repeated database queries.

Conceptual cache key:

```text
tasks:{user_id}:{query_parameters}
```

Task creation, update and deletion invalidate relevant cached responses.

The current implementation uses user scoped invalidation.

## Celery Background Jobs

Celery handles asynchronous operations such as task reassignment notifications and overdue task processing.

```text
Task Update
    │
    ▼
Database Update
    │
    ▼
Queue Celery Task
    │
    ▼
HTTP Response
    │
    ▼
Celery Worker
    │
    ▼
Create Notification
```

## Error Handling

| Code | Meaning                           |
| ---: | --------------------------------- |
|  200 | Successful operation              |
|  201 | Resource created                  |
|  400 | Invalid request                   |
|  401 | Invalid or missing authentication |
|  403 | Permission denied                 |
|  404 | Resource not found                |
|  409 | Resource conflict                 |
|  422 | Validation error                  |
|  500 | Internal server error             |

## Security

| Measure        | Implementation        |
| -------------- | --------------------- |
| Authentication | JWT                   |
| Passwords      | bcrypt hashing        |
| Authorization  | Bearer tokens         |
| Secrets        | Environment variables |
| Validation     | FastAPI schemas       |
| Database       | SQLAlchemy ORM        |
| Production     | HTTPS                 |

Use a strong `SECRET_KEY` and never expose credentials in source control.

## Deployment

**Note for Reviewer:** For the deployment deliverable, I have chosen the **documented/scripted deployment path** option rather than a live URL, to easily spin up the complete stack (including background workers) without being restricted by cloud provider free-tier limitations.

### Scripted Deployment (Docker Compose)

The repository includes a `deploy.sh` script that automates the deployment of the full stack (FastAPI, PostgreSQL, Redis, and Celery Workers) to any VM or Linux server with Docker installed.

1. Make the script executable:
   ```bash
   chmod +x deploy.sh
   ```

2. Run the deployment script:
   ```bash
   ./deploy.sh
   ```

The script will automatically:
1. Pull the latest code.
2. Build the Docker images.
3. Bring up the entire stack in the background using Docker Compose.
4. Run Alembic database migrations.

### Cloud Deployment (Render)

If you still prefer to deploy to a cloud provider like Render, a `render.yaml` blueprint is included. Due to Render's free tier limitations (which do not support background workers natively), we consolidated the Celery workers into the main web service container via an `entrypoint.sh` script.

To deploy on Render:
1. Connect this repository to your Render account.
2. Create a New Web Service.
3. Render will use the provided `Dockerfile` and `entrypoint.sh` to start the web server and background workers together in a single instance.

## Production Architecture

```text
                    Internet
                       │
                       ▼
                Load Balancer
                       │
                       ▼
              FastAPI Web Service
                 /          \
                ▼            ▼
          PostgreSQL        Redis
                            │
                            ▼
                      Celery Worker
```

## Performance

| Area         | Current             | Future             |
| ------------ | ------------------- | ------------------ |
| Task Queries | Database queries    | Composite indexes  |
| Task Listing | Redis cache         | Cache tagging      |
| Pagination   | Offset              | Cursor pagination  |
| Jobs         | Celery              | Multiple queues    |
| Cache        | User scoped         | Event driven       |
| Database     | PostgreSQL          | Read replicas      |
| Metrics      | Application metrics | Prometheus/Grafana |

## Tradeoffs & Improvements

### Cache Invalidation

Current invalidation is user scoped. A more granular strategy could use Redis `SCAN`, cache tagging or tracked cache keys instead of broad invalidation.

### Notifications

Notifications are currently stored in the database. Production could integrate email or SMS providers with retries, delivery status and user preferences.

### Database Migrations

Running migrations during application startup can cause race conditions with multiple replicas. A dedicated migration job or release phase is preferable.

### Pagination

Offset pagination is simple but can become inefficient for large datasets. Cursor based pagination would scale better.

### Celery Beat

A production setup can add Celery Beat to run overdue task checks periodically.

```text
Celery Beat
    ↓
Every Hour
    ↓
check_overdue_tasks
    ↓
Create Notifications
```

## API Usage Flow

```text
Signup
  ↓
Login
  ↓
Receive JWT
  ↓
Create Project
  ↓
Create Task
  ↓
Filter Tasks
  ↓
Update Task
  ↓
Celery Notification
  ↓
Get Notifications
```

## Development Workflow

```text
Create Branch
     ↓
Implement Feature
     ↓
Add Tests
     ↓
Run Pytest
     ↓
Run Docker Compose
     ↓
Verify Swagger
     ↓
Create Pull Request
     ↓
Deploy
```

## Monitoring

| Check            | Location    |
| ---------------- | ----------- |
| API Availability | `/health`   |
| PostgreSQL       | `/health`   |
| Redis            | `/health`   |
| Requests         | `/metrics`  |
| Errors           | `/metrics`  |
| Response Time    | `/metrics`  |
| Celery           | Worker Logs |
| Migrations       | Alembic     |

## Documentation

| Resource   | Location        |
| ---------- | --------------- |
| Swagger UI | `/docs`         |
| ReDoc      | `/redoc`        |
| OpenAPI    | `/openapi.json` |
| Health     | `/health`       |
| Metrics    | `/metrics`      |

## License

TaskFlow is a backend engineering project demonstrating REST API design, authentication, database management, caching, asynchronous processing, testing and deployment practices.
