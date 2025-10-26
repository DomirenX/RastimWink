# -*- coding: utf-8 -*-
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from app.database import get_db, engine, Base
from app import models
from app.schemas import user, task, notification
from app.crud import user as user_crud, task as task_crud, notification as notification_crud
from app.auth import authenticate_user, create_access_token, get_current_user, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.user import UserRole

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wink Internal API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth
@app.post("/api/auth/login")
def login(user_data: user.UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user_data.email, user_data.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user": db_user}

# Tasks
@app.get("/api/tasks")
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role in [UserRole.hr, UserRole.manager, UserRole.admin]:
        tasks = task_crud.get_tasks(db, skip=skip, limit=limit)
    else:
        tasks = task_crud.get_user_tasks(db, current_user.id)
    return tasks

@app.post("/api/tasks")
def create_task(
    task_data: task.TaskCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [UserRole.hr, UserRole.manager, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_task = task_crud.create_task(db, task_data, current_user.id)
    
    # Create notification
    notification_data = notification.NotificationBase(
        title="New task",
        message=f"You have new task: {task_data.title}",
        type="new_task",
        related_entity_id=db_task.id
    )
    notification_crud.create_notification(db, notification_data, task_data.assignee_id)
    
    return db_task

@app.get("/")
def read_root():
    return {"message": "Wink Internal API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)