from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import datetime

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True) # transportation, food, energy
    description = Column(String)
    value = Column(Float) # e.g. km traveled, kWh used
    carbon_emission = Column(Float) # calculated kg CO2
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
