from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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

SECRET_KEY = "krasnodiplomshik"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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
    comments_required: bool = False
    min_comments: int = 5
    comments_received: int = 0

class Idea(BaseModel):
    id: int
    title: str
    description: str
    author_id: int
    status: str = "pending"

class EmployeeComment(BaseModel):
    id: int
    task_id: int
    employee_id: int
    comment: str
    created_at: str
    employee_name: str = ""

class ManagerReview(BaseModel):
    id: int
    task_id: int
    manager_id: int
    comment: str
    rating: float
    created_at: str
    manager_name: str = ""

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

mock_users = [
    User(id=1, email="admin@wink.com", full_name="Admin User", role=UserRole.admin, department_id=1),
    User(id=2, email="manager@wink.com", full_name="Manager User", role=UserRole.manager, department_id=1),
    User(id=3, email="employee1@wink.com", full_name="Employee One", role=UserRole.employee, department_id=2),
    User(id=4, email="employee2@wink.com", full_name="Employee Two", role=UserRole.employee, department_id=2),
    User(id=5, email="employee3@wink.com", full_name="Employee Three", role=UserRole.employee, department_id=2),
    User(id=6, email="employee4@wink.com", full_name="Employee Four", role=UserRole.employee, department_id=2),
    User(id=7, email="employee5@wink.com", full_name="Employee Five", role=UserRole.employee, department_id=2),
]

mock_tasks = [
    Task(id=1, title="Setup database", description="Initialize PostgreSQL", assignee_id=3, creator_id=2, status="in_progress", priority="high", created_at="2024-01-01"),
    Task(id=2, title="Create API", description="Build REST endpoints", assignee_id=3, creator_id=2, status="pending", priority="critical", created_at="2024-01-01"),
]

mock_ideas = []
mock_comments = []
mock_manager_reviews = []

user_password_hashes = {
    "admin@wink.com": get_password_hash("admin123"),
    "manager@wink.com": get_password_hash("manager123"),
    "employee1@wink.com": get_password_hash("employee123"),
    "employee2@wink.com": get_password_hash("employee123"),
    "employee3@wink.com": get_password_hash("employee123"),
    "employee4@wink.com": get_password_hash("employee123"),
    "employee5@wink.com": get_password_hash("employee123"),
}

def get_user_by_email(email: str) -> Optional[User]:
    return next((u for u in mock_users if u.email == email), None)

def authenticate_user(email: str, password: str) -> Optional[User]:
    user = get_user_by_email(email)
    if not user:
        return None
    
    hashed_password = user_password_hashes.get(email)
    if not hashed_password or not verify_password(password, hashed_password):
        return None
    
    return user

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

@app.get("/")
def root():
    return {
        "message": "Wink Internal API - WORKING!",
        "version": "1.1",
        "features": ["tasks", "ideas", "comments_system", "analytics", "auth"]
    }

@app.post("/api/auth/login", response_model=Token)
def login(user_data: UserLogin):
    user = authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.get("/api/tasks")
def get_tasks(current_user: User = Depends(get_current_user)):
    return mock_tasks

@app.get("/api/tasks/{task_id}")
def get_task(task_id: int, current_user: User = Depends(get_current_user)):
    task = next((t for t in mock_tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/api/tasks")
def create_task(task: Task, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.manager, UserRole.hr, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Only managers can create tasks")
    
    new_id = max([t.id for t in mock_tasks]) + 1 if mock_tasks else 1
    task.id = new_id
    task.created_at = datetime.now().isoformat()
    task.creator_id = current_user.id
    mock_tasks.append(task)
    return task

@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, task_update: dict, current_user: User = Depends(get_current_user)):
    task = next((t for t in mock_tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if current_user.role == UserRole.employee and task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only update own tasks")
    
    for key, value in task_update.items():
        if hasattr(task, key):
            setattr(task, key, value)
    return task

@app.post("/api/tasks/{task_id}/assign-commenters")
def assign_commenters(
    task_id: int,
    commenter_ids: List[int],
    current_user: User = Depends(get_current_user)
):
    """Назначить 5 сотрудников для комментариев к задаче"""
    if current_user.role not in [UserRole.manager, UserRole.hr, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Only managers can assign commenters")
    
    if len(commenter_ids) != 5:
        raise HTTPException(status_code=400, detail="Exactly 5 commenters required")
    
    task = next((t for t in mock_tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    for user_id in commenter_ids:
        user = next((u for u in mock_users if u.id == user_id), None)
        if not user or user.role != UserRole.employee:
            raise HTTPException(status_code=400, detail=f"User {user_id} is not an employee")
    
    task.comments_required = True
    task.min_comments = 5
    
    return {
        "task_id": task_id,
        "assigned_commenters": commenter_ids,
        "message": "5 employees assigned for comments"
    }

@app.post("/api/tasks/{task_id}/comments")
def add_employee_comment(
    task_id: int,
    comment_data: dict,
    current_user: User = Depends(get_current_user)
):
    task = next((t for t in mock_tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not task.comments_required:
        raise HTTPException(status_code=400, detail="This task doesn't require comments")
    
    if "comment" not in comment_data or not comment_data["comment"].strip():
        raise HTTPException(status_code=400, detail="Comment text is required")
    
    new_comment = EmployeeComment(
        id=len(mock_comments) + 1,
        task_id=task_id,
        employee_id=current_user.id,
        comment=comment_data["comment"].strip(),
        created_at=datetime.now().isoformat(),
        employee_name=current_user.full_name
    )
    
    mock_comments.append(new_comment)
    
    task.comments_received += 1
    
    return new_comment

@app.get("/api/tasks/{task_id}/comments")
def get_task_comments(task_id: int, current_user: User = Depends(get_current_user)):
    """Получить все комментарии для задачи"""
    task = next((t for t in mock_tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_comments = [c for c in mock_comments if c.task_id == task_id]
    manager_review = next((r for r in mock_manager_reviews if r.task_id == task_id), None)
    
    comments_stats = {
        "total_comments": len(task_comments),
        "required_comments": task.min_comments,
        "completion_percentage": round((len(task_comments) / task.min_comments) * 100, 2) if task.min_comments > 0 else 0
    }
    
    return {
        "task": task,
        "employee_comments": task_comments,
        "manager_review": manager_review,
        "comments_stats": comments_stats
    }

@app.post("/api/tasks/{task_id}/manager-review")
def submit_manager_review(
    task_id: int,
    review_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Комментарий и оценка от начальника"""
    if current_user.role not in [UserRole.manager, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Only managers can provide reviews")
    
    task = next((t for t in mock_tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if "comment" not in review_data or "rating" not in review_data:
        raise HTTPException(status_code=400, detail="Comment and rating are required")
    
    task_comments = [c for c in mock_comments if c.task_id == task_id]
    if len(task_comments) < task.min_comments:
        raise HTTPException(
            status_code=400, 
            detail=f"Need at least {task.min_comments} comments, got {len(task_comments)}"
        )
    
    rating = review_data["rating"]
    if rating < 1 or rating > 10:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 10")
    
    manager_review = ManagerReview(
        id=len(mock_manager_reviews) + 1,
        task_id=task_id,
        manager_id=current_user.id,
        comment=review_data["comment"],
        rating=rating,
        created_at=datetime.now().isoformat(),
        manager_name=current_user.full_name
    )
    
    mock_manager_reviews.append(manager_review)
    
    task.status = TaskStatus.completed
    
    return manager_review

@app.get("/api/users/{user_id}/pending-comments")
def get_pending_comments(user_id: int, current_user: User = Depends(get_current_user)):
    """Получить список задач, где сотрудник должен оставить комментарий"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only view own pending comments")
    
    pending_tasks = []
    for task in mock_tasks:
        if task.comments_required and task.status != TaskStatus.completed:
            existing_comment = next((c for c in mock_comments if c.task_id == task.id and c.employee_id == user_id), None)
            if not existing_comment:
                pending_tasks.append(task)
    
    return pending_tasks

@app.get("/api/ideas")
def get_ideas(current_user: User = Depends(get_current_user)):
    return mock_ideas

@app.post("/api/ideas")
def create_idea(idea: Idea, current_user: User = Depends(get_current_user)):
    new_id = len(mock_ideas) + 1
    idea.id = new_id
    idea.author_id = current_user.id
    mock_ideas.append(idea)
    return idea

@app.put("/api/ideas/{idea_id}/status")
def update_idea_status(idea_id: int, status: str, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.manager, UserRole.hr, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Only managers can update idea status")
    
    idea = next((i for i in mock_ideas if i.id == idea_id), None)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    idea.status = status
    return idea

@app.get("/api/analytics/tasks")
def get_task_analytics(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.hr, UserRole.manager, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    total_tasks = len(mock_tasks)
    completed = len([t for t in mock_tasks if t.status == "completed"])
    in_progress = len([t for t in mock_tasks if t.status == "in_progress"])
    
    return {
        "total_tasks": total_tasks,
        "completed": completed,
        "in_progress": in_progress,
        "completion_rate": round((completed / total_tasks * 100), 2) if total_tasks > 0 else 0
    }

@app.get("/api/analytics/employee-performance")
def get_employee_performance(current_user: User = Depends(get_current_user)):
    """Аналитика производительности сотрудников по оценкам менеджеров"""
    if current_user.role not in [UserRole.hr, UserRole.manager, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    performance_data = {}
    
    for task in mock_tasks:
        if task.status == TaskStatus.completed:
            manager_review = next((r for r in mock_manager_reviews if r.task_id == task.id), None)
            if manager_review and task.assignee_id:
                if task.assignee_id not in performance_data:
                    employee = next((u for u in mock_users if u.id == task.assignee_id), None)
                    performance_data[task.assignee_id] = {
                        "employee_name": employee.full_name if employee else "Unknown",
                        "total_tasks": 0,
                        "average_rating": 0,
                        "ratings": []
                    }
                
                performance_data[task.assignee_id]["total_tasks"] += 1
                performance_data[task.assignee_id]["ratings"].append(manager_review.rating)
    
    for employee_id, data in performance_data.items():
        if data["ratings"]:
            data["average_rating"] = round(sum(data["ratings"]) / len(data["ratings"]), 2)
    
    return performance_data

@app.get("/api/health")
def health_check():
    return {
        "status": "OK", 
        "database": "mock", 
        "tasks_count": len(mock_tasks),
        "ideas_count": len(mock_ideas),
        "comments_count": len(mock_comments),
        "manager_reviews_count": len(mock_manager_reviews),
        "features": ["auth", "tasks", "ideas", "comments_system", "analytics"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)