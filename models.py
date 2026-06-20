from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    monthly_goal = Column(Float, default=150.0) # default kg CO2 per month

    logs = relationship("ActivityLog", back_populates="owner")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True) # transportation, food, energy
    description = Column(String)
    value = Column(Float) # e.g. km traveled, kWh used
    carbon_emission = Column(Float) # calculated kg CO2
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="logs")
