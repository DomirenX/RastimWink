from time import timezone
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class TaskStatus(enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    rejected = "rejected"
    under_review = "under_review"

class TaskPriority(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key = True, index = True)
    title = Column(String, nullable = False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default = TaskStatus.pending, nullable = False)
    priority = Column(Enum(TaskPriority), default = TaskPriority.medium, nullable = False)
    assignee_id = Column(Integer, ForeignKey("departments.id"))
    creator_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    created_at = Column(DateTime(timezone = True), server_default = func.now())
    updated_at = Column(DateTime(timezone = True), onupdate = func.now())
    deadline = Column(DateTime(timezone = True))
    comments_required = Column(Boolean, default = False)
    min_comments = Column(Integer, default = 5)
    comments_received = Column(Integer, default = 0)
    is_quantitative = Column(Boolean, default = False)
    goal_target = Column(Float, nullable = True)
    goal_progress = Column(Float, nullable = True)
    completed_at = Column(DateTime(timezone = True))

    assignee = relationship("User", foreign_keys = [assignee_id], back_populates = "tasks_assigned")
    creator = relationship("User", foreign_keys = [creator_id], back_populates = "tasks_created")
    department = relationship("Department", back_populates = "tasks")
    employee_comments = relationship("EmployeeComment", back_populates = "task")
    manager_review = relationship("ManagerReview", back_populates = "task", uselist = False)
    subtasks = relationship("Subtask", back_populates = "task", uselist = False)