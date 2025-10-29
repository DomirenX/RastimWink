from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class EmployeeCommentBase(BaseModel):
    comment: str

class EmployeeCommentCreate(EmployeeCommentBase):
    task_id: int

class EmployeeCommentResponse(EmployeeCommentBase):
    id: int
    task_id: int
    employee_id: int
    employee_name: str
    created_at: datetime

class ManagerReviewBase(BaseModel):
    comment: str
    rating: float

class ManagerReviewCreate(ManagerReviewBase):
    task_id: int

class ManagerReviewResponse(ManagerReviewBase):
    id: int
    task_id: int
    manager_id: int
    manager_name: str
    created_at: datetime

class TaskWithCommentsResponse(BaseModel):
    task: dict
    employee_comments: List[EmployeeCommentResponse]
    manager_review: Optional[ManagerReviewResponse] = None
    comments_stats: dict