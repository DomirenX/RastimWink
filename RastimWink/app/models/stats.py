from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class EmployeeStats(Base):
    __tablename__ = "employee_stats"

    id = Column(Integer, primary_key = True, index = True)
    employee_id = Column(Integer, ForeignKey("users.id"), unique = True, nullable = False)
    total_tasks_completed = Column(Integer, default = 0)
    average_rating = Column(Float, default = 0.0)
    total_rating = Column(Float, default = 0.0)
    rating_count = Column(Integer, default = 0)
    last_activity = Column(DateTime(timezone = True))
    created_at = Column(DateTime(timezone = True), server_default = func.now())
    updated_at = Column(DateTime(timezone = True), onupdate = func.now())

    employee = relationship("User")

class EmployeeInvitation(Base):
    __tablename__ = "employee_invitations"

    id = Column(Integer, primary_key = True, index = True)
    email = Column(String, nullable = False)
    corporate_email = Column(String, nullable = False)
    token = Column(String, unique = True, nullable = False)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable = False)
    is_activated = Column(Boolean, default = False)
    activated_at = Column(DateTime(timezone = True))
    created_at = Column(DateTime(timezone = True), server_default = func.now())
    expires_at = Column(DateTime(timezone = True))