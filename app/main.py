from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time

from app.api.v1 import auth, projects, tasks
from app.core.config import settings
from app.core.database import engine, Base
from app.core.redis import get_redis

# Create tables (In a real app, use Alembic. We keep it for simplicity if no migrations are run)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# Basic metrics storage
metrics_data = {
    "total_requests": 0,
    "total_errors": 0,
    "response_times": []
}

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    metrics_data["total_requests"] += 1
    start_time = time.time()
    try:
        response = await call_next(request)
        if response.status_code >= 400:
            metrics_data["total_errors"] += 1
        return response
    except Exception as e:
        metrics_data["total_errors"] += 1
        raise e
    finally:
        process_time = time.time() - start_time
        metrics_data["response_times"].append(process_time)
        # keep last 1000 to avoid memory leak
        if len(metrics_data["response_times"]) > 1000:
            metrics_data["response_times"].pop(0)

@app.get("/health")
def health_check():
    health_status = {"status": "ok"}
    try:
        get_redis().ping()
        health_status["redis"] = "up"
    except Exception:
        health_status["redis"] = "down"
        health_status["status"] = "degraded"
        
    try:
        # Simple DB ping
        with engine.connect() as conn:
            pass
        health_status["db"] = "up"
    except Exception:
        health_status["db"] = "down"
        health_status["status"] = "degraded"
        
    return health_status

@app.get("/metrics")
def get_metrics():
    avg_time = sum(metrics_data["response_times"]) / len(metrics_data["response_times"]) if metrics_data["response_times"] else 0
    return {
        "total_requests": metrics_data["total_requests"],
        "total_errors": metrics_data["total_errors"],
        "avg_response_time_seconds": avg_time
    }

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(projects.router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"])
app.include_router(tasks.router, prefix=f"{settings.API_V1_STR}/tasks", tags=["tasks"])
