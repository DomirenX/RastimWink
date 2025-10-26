from email.policy import default
from app.crud import notification
from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class UserRole(enum.Enum):
    employee = "employee"
    manager = "manager"
    hr = "hr"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index = True)
    email = Column(String, unique = True, index = True, nullable = False)
    password_hash = Column(String, nullable = False)
    full_name = Column(String, nullable = False)
    role = Column(Enum(UserRole), default = UserRole.employee, nullable = False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    is_active = Column(Boolean, default = True)
    created_at = Column(DateTime(timezone = True), server_default = func.now())

    department = relationship("Department", back_populates = "user")
    tasks_created = relationship("Task", foreign_keys = "Task.creator_id", back_populates = "creator")
    task_assigned = relationship("Task", foreign_keys = "Task.assignee_id", back_populates = "assignee")
    notifications = relationship("Notification", back_populates = "user")