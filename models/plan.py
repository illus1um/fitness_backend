from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.session import Base
import datetime

class Plan(Base):
    __tablename__ = "training_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    days = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="plan")

    def to_dict(self):
        """Конвертирует объект в словарь для API"""
        return {
            "start_date": self.start_date.isoformat(),
            "days": self.days  # Возвращаем как есть, так как уже в правильном формате
        }