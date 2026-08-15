import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.schemas.response import APIResponse
from app.core.redis import get_redis
from app.worker.tasks import create_notification

router = APIRouter()

def invalidate_tasks_cache(user_id: int, redis_client):
    keys = redis_client.keys(f"tasks:{user_id}:*")
    if keys:
        redis_client.delete(*keys)

@router.post("/", response_model=APIResponse[TaskResponse], status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == task_in.project_id).first()
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions or project not found")
    
    task = Task(**task_in.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    
    invalidate_tasks_cache(current_user.id, get_redis())
    return APIResponse(message="Task created successfully!", status="success", code=201, data=task)

@router.get("/", response_model=APIResponse[List[TaskResponse]])
def read_tasks(
    status: Optional[TaskStatus] = None,
    assignee: Optional[str] = None,
    due_date_start: Optional[datetime] = None,
    due_date_end: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    redis_client = get_redis()
    cache_key = f"tasks:{current_user.id}:status={status}:assignee={assignee}:start={due_date_start}:end={due_date_end}:skip={skip}:limit={limit}"
    
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return APIResponse(message="Tasks retrieved successfully from cache!", status="success", code=200, data=json.loads(cached_data))

    query = db.query(Task).join(Project).filter(Project.owner_id == current_user.id)
    
    if status:
        query = query.filter(Task.status == status)
    if assignee:
        query = query.filter(Task.assignee == assignee)
    if due_date_start:
        query = query.filter(Task.due_date >= due_date_start)
    if due_date_end:
        query = query.filter(Task.due_date <= due_date_end)
        
    tasks = query.offset(skip).limit(limit).all()
    
    # Serialize to dict for cache
    tasks_data = []
    for task in tasks:
        task_dict = {
            "title": task.title,
            "description": task.description,
            "status": task.status.value,
            "assignee": task.assignee,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "id": task.id,
            "project_id": task.project_id
        }
        tasks_data.append(task_dict)
        
    redis_client.setex(cache_key, 300, json.dumps(tasks_data))
    return APIResponse(message="Tasks retrieved successfully!", status="success", code=200, data=tasks)

@router.get("/{task_id}", response_model=APIResponse[TaskResponse])
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).join(Project).filter(Task.id == task_id, Project.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return APIResponse(message="Task retrieved successfully!", status="success", code=200, data=task)

@router.put("/{task_id}", response_model=APIResponse[TaskResponse])
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).join(Project).filter(Task.id == task_id, Project.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_in.model_dump(exclude_unset=True)
    
    old_assignee = task.assignee
    
    for field, value in update_data.items():
        setattr(task, field, value)
        
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Check if we need to trigger a notification
    if "assignee" in update_data and old_assignee != task.assignee and task.assignee is not None:
        create_notification.delay(task.id, f"Task reassigned to {task.assignee}")

    invalidate_tasks_cache(current_user.id, get_redis())
    return APIResponse(message="Task updated successfully!", status="success", code=200, data=task)

@router.delete("/{task_id}", response_model=APIResponse[None])
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).join(Project).filter(Task.id == task_id, Project.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    invalidate_tasks_cache(current_user.id, get_redis())
    return APIResponse(message="Task deleted successfully!", status="success", code=200, data=None)
