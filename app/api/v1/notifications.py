from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.notification import Notification
from app.models.task import Task
from app.models.project import Project
from app.schemas.notification import NotificationResponse
from app.schemas.response import APIResponse

router = APIRouter()

@router.get("/", response_model=APIResponse[List[NotificationResponse]])
def get_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Only get notifications for tasks belonging to the current user's projects
    notifications = db.query(Notification)\
        .join(Task, Notification.task_id == Task.id)\
        .join(Project, Task.project_id == Project.id)\
        .filter(Project.owner_id == current_user.id)\
        .order_by(Notification.created_at.desc())\
        .all()
    
    return APIResponse(message="Notifications retrieved successfully!", status="success", code=200, data=notifications)
