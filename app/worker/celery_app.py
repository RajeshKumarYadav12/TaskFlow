from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.worker.tasks']
)



from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "check-overdue-tasks-every-hour": {
        "task": "app.worker.tasks.check_overdue_tasks",
        "schedule": crontab(minute=0, hour="*"),
    },
}
