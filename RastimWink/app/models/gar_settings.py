from sqlalchemy import Column, Integer, Float
from app.database import Base

class GARSettings(Base):
    __tablename__ = "gar_settings"
    id = Column(Integer, primary_key=True, index=True)
    w_tcr = Column(Float, default=0.4)
    w_goal = Column(Float, default=0.3)
    w_timeliness = Column(Float, default=0.2)
    w_quality = Column(Float, default=0.1)
