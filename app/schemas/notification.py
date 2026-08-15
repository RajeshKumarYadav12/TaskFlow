from pydantic import BaseModel
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    task_id: int
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
