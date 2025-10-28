from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import enum
import hashlib
import jwt
from datetime import datetime, timedelta

app = FastAPI(title="Wink Internal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple enums
class UserRole(str, enum.Enum):
    employee = "employee"
    manager = "manager"
    hr = "hr"
    admin = "admin"

class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    under_review = "under_review"

class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

# Models
class User(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    department_id: Optional[int] = None

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.pending
    priority: TaskPriority = TaskPriority.medium
    assignee_id: int
    creator_id: int
    created_at: Optional[str] = None

class Idea(BaseModel):
    id: int
    title: str
    description: str
    author_id: int
    status: str = "pending"

class UserLogin(BaseModel):
    email: str
    password: str

# Mock data
mock_users = [
    User(id=1, email="admin@wink.com", full_name="Admin User", role=UserRole.admin, department_id=1),
    User(id=2, email="manager@wink.com", full_name="Manager User", role=UserRole.manager, department_id=1),
    User(id=3, email="employee@wink.com", full_name="Employee User", role=UserRole.employee, department_id=2),
]

mock_tasks = [
    Task(id=1, title="Setup database", description="Initialize PostgreSQL", assignee_id=3, creator_id=2, status="pending", priority="high", created_at="2024-01-01"),
    Task(id=2, title="Create API", description="Build REST endpoints", assignee_id=3, creator_id=2, status="in_progress", priority="critical", created_at="2024-01-01"),
]

mock_ideas = []
clicker_counts = {}
user_passwords = {
    "admin@wink.com": "admin123", 
    "manager@wink.com": "manager123", 
    "employee@wink.com": "employee123"
}

# Simple auth functions
SECRET_KEY = "wink-secret-key-2024"

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def get_user_by_email(email: str) -> Optional[User]:
    return next((u for u in mock_users if u.email == email), None)

def authenticate_user(email: str, password: str) -> Optional[User]:
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user_passwords.get(email, "")):
        return None
    return user

# API endpoints
@app.get("/")
def root():
    return {
        "message": "Wink Internal API - WORKING!",
        "version": "1.0",
        "features": ["tasks", "ideas", "chill_zone", "analytics", "auth"]
    }

# Auth endpoints
@app.post("/api/auth/login")
def login(user_data: UserLogin):
    user = authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

# Tasks API
@app.get("/api/tasks")
def get_tasks():
    return mock_tasks

@app.get("/api/tasks/{task_id}")
def get_task(task_id: int):
    task = next((t for t in mock_tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/api/tasks")
def create_task(task: Task):
    new_id = max([t.id for t in mock_tasks]) + 1 if mock_tasks else 1
    task.id = new_id
    task.created_at = datetime.now().isoformat()
    mock_tasks.append(task)
    return task

@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, task_update: dict):
    task = next((t for t in mock_tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    for key, value in task_update.items():
        if hasattr(task, key):
            setattr(task, key, value)
    return task

# Ideas System (YOUR FEATURE!)
@app.get("/api/ideas")
def get_ideas():
    return mock_ideas

@app.post("/api/ideas")
def create_idea(idea: Idea):
    new_id = len(mock_ideas) + 1
    idea.id = new_id
    mock_ideas.append(idea)
    return idea

@app.put("/api/ideas/{idea_id}/status")
def update_idea_status(idea_id: int, status: str):
    idea = next((i for i in mock_ideas if i.id == idea_id), None)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    idea.status = status
    return idea

# Chill Zone (YOUR FEATURE!)
@app.get("/api/chill/clicker/{user_id}")
def get_clicker_count(user_id: int):
    return {"clicks": clicker_counts.get(user_id, 0)}

@app.post("/api/chill/click/{user_id}")
def increment_clicker(user_id: int):
    current = clicker_counts.get(user_id, 0)
    clicker_counts[user_id] = current + 1
    return {"clicks": current + 1}

# Analytics
@app.get("/api/analytics/tasks")
def get_task_analytics():
    total_tasks = len(mock_tasks)
    completed = len([t for t in mock_tasks if t.status == "completed"])
    in_progress = len([t for t in mock_tasks if t.status == "in_progress"])
    
    return {
        "total_tasks": total_tasks,
        "completed": completed,
        "in_progress": in_progress,
        "completion_rate": round((completed / total_tasks * 100), 2) if total_tasks > 0 else 0
    }

@app.get("/api/analytics/ideas")
def get_idea_analytics():
    total_ideas = len(mock_ideas)
    approved = len([i for i in mock_ideas if i.status == "approved"])
    
    return {
        "total_ideas": total_ideas,
        "approved": approved,
        "approval_rate": round((approved / total_ideas * 100), 2) if total_ideas > 0 else 0
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "OK", 
        "database": "mock", 
        "tasks_count": len(mock_tasks),
        "ideas_count": len(mock_ideas),
        "users_count": len(mock_users),
        "features": ["auth", "tasks", "ideas", "chill_zone", "analytics"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)