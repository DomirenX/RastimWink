from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class EmployeeStatsBase(BaseModel):
    total_tasks_completed: int
    average_rating: float
    last_activity: Optional[datetime] = None

class EmployeeStatsResponse(EmployeeStatsBase):
    employee_id: int
    employee_name: str
    employee_email: str

class TaskWithRating(BaseModel):
    id: int
    title: str
    completed_at: datetime
    manager_rating: float
    manager_comment: str

class EmployeeDetailedStats(EmployeeStatsBase):
    employee_id: int
    employee_name: str
    employee_email: str
    recent_tasks: List[TaskWithRating]
    perfomance_trend: List[float]

class HRDashboard(BaseModel):
    total_employees: int
    active_employees: int
    average_company_rating: float
    total_tasks_completed: int
    top_performers: List[EmployeeStatsResponse]
    recent_activity: List[dict]

class InvitationCreate(BaseModel):
    email: str
    full_name: str
    department_id: Optional[int] = None

class InvitationResponse(BaseModel):
    id: int
    email: str
    corporate_email: str
    invited_by: int
    created_at: datetime
    expires_at: datetime
    is_actived: bool

class PasswordSetup(BaseModel):
    token: str
    password: str