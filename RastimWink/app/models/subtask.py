from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Subtask(Base):
    __tablename__ = "subtasks"

    id = Column(Integer, primary_key = True, index = True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable = False)
    title = Column(String, nullable = False)
    weight = Column(Float, default = 1.0)

    task = relationship("Task", back_populates = "subtasks")