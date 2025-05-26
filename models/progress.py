import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base

class Progress(Base):
    __tablename__ = "training_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day_index = Column(Integer, nullable=False)
    exercise_id = Column(String, nullable=False)
    sets_completed = Column(Integer, default=0, nullable=False)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # relationship with user
    user = relationship("User", back_populates="progress")
