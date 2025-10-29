from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class EmployeeComment(Base):
    __tablename__ = "employee_comments"

    id = Column(Integer, primary_key = True, index = True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable = False)
    empoyee_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    comment = Column(Text, nullable = False)
    created_at = Column(DateTime(timezone = True), server_default = func.now())

    task = relationship("User", back_populates = "comments_given")

class ManagerReview(Base):
    __tablename__ = "manager_reviews"

    id = Column(Integer, primary_key = True, index = True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable = False, unique = True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    comment = Column(Text)
    rating = Column(Float)
    created_at = Column(DateTime(timezone = True), server_default = func.now())

    task = relationship("Task", back_populates = "manager_review")
    manager = relationship("User")