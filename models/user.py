from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from database.session import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(Boolean, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    age = Column(Integer, nullable=True)
    training_program = Column(String, nullable=True)
    training_location = Column(String, nullable=True)
    training_experience = Column(String, nullable=True)
    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    plan = relationship("Plan", back_populates="user", uselist=False, cascade="all, delete-orphan")
    water_intake = relationship("WaterIntake", back_populates="user", cascade="all, delete-orphan")
    water_intake_records = relationship("WaterIntakeRecord", back_populates="user", cascade="all, delete-orphan")
    avatar_url = Column(String, nullable=True)

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)