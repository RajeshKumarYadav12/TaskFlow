from app.core.database import Base
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.notification import Notification

# This allows Alembic to easily import all models
__all__ = ["Base", "User", "Project", "Task", "Notification"]
