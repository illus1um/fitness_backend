from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class WaterIntakeRecordCreate(BaseModel):
    amount: float
    timestamp: datetime


class WaterIntakeRecord(BaseModel):
    id: int
    amount: float
    timestamp: datetime

    class Config:
        from_attributes = True


class WaterIntakeBase(BaseModel):
    date: str
    amount: float


class WaterIntakeCreate(WaterIntakeBase):
    pass


class WaterIntake(WaterIntakeBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class DailyWaterIntakeResponse(BaseModel):
    date: str
    total_amount: float
    records: List[WaterIntakeRecord]

    class Config:
        from_attributes = True


class WaterIntakeHistoryResponse(BaseModel):
    history: List[WaterIntakeBase]

    class Config:
        from_attributes = True


class WaterIntakeRequest(BaseModel):
    amount: float
    records: Optional[List[WaterIntakeRecordCreate]] = None