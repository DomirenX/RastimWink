from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, unique = True, index = True, nullable = False)

    users = relationship("User", back_populates = "department")
    tasks = relationship("Task", back_populates = "department")