import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from database.session import Base


class WaterIntake(Base):
    __tablename__ = "water_intake"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(String, nullable=False)  # Format: YYYY-MM-DD
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationship with User model
    user = relationship("User", back_populates="water_intake")


class WaterIntakeRecord(Base):
    __tablename__ = "water_intake_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(String, nullable=False)  # Format: YYYY-MM-DD
    timestamp = Column(DateTime, nullable=False)

    # Relationship with User model
    user = relationship("User", back_populates="water_intake_records")