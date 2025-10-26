from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primaty_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    title = Column(String, nullable = False)
    message = Column(String, nullable = False)
    type = Column(String, nullable = False)
    is_read = Column(Boolean, default = False)
    related_entity_id = Column(Integer)
    created_id = Column(DateTime(timezone = True), server_default = func.now())

    user = relationship("User", back_populates = "notifications")