import json
from datetime import datetime
from app.worker.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.notification import Notification

@celery_app.task
def create_notification(task_id: int, message: str):
    print(f"Simulating sending notification for task {task_id}: {message}")
    db = SessionLocal()
    try:
        notification = Notification(task_id=task_id, message=message)
        db.add(notification)
        db.commit()
    finally:
        db.close()
    return f"Notification created for task {task_id}"

@celery_app.task
def check_overdue_tasks():
    print("Checking for overdue tasks...")
    db = SessionLocal()
    try:
        from app.models.task import Task, TaskStatus
        now = datetime.utcnow()
        overdue_tasks = db.query(Task).filter(
            Task.due_date < now,
            Task.status != TaskStatus.done
        ).all()
        for task in overdue_tasks:
            # Check if we already notified recently to avoid spam (simplification: we just notify)
            message = f"Task '{task.title}' is overdue!"
            create_notification.delay(task.id, message)
    finally:
        db.close()
    return "Finished checking overdue tasks"
