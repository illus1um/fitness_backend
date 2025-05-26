from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, validator
import logging

logger = logging.getLogger(__name__)


class Exercise(BaseModel):
    id: str
    name: str
    sets: int
    reps: Any
    rest: Optional[str] = None
    restSec: Optional[int] = None
    notes: Optional[str] = None

    bodyPart: Optional[str] = None
    equipment: Optional[str] = None
    gifUrl: Optional[str] = None
    target: Optional[str] = None
    secondaryTargets: Optional[List[str]] = None
    instructions: Optional[List[str]] = None
    programs: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    experienceLevels: Optional[List[str]] = None
    durationSec: Optional[int] = None

    class Config:
        extra = "allow"
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DayInfo(BaseModel):
    dayIndex: int
    part: str
    exercises: List[Exercise]

    class Config:
        extra = "allow"
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PlanCreate(BaseModel):
    start_date: datetime
    days: List[DayInfo]

    class Config:
        extra = "allow"
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PlanOut(BaseModel):
    start_date: datetime
    days: List[DayInfo]

    class Config:
        orm_mode = True
        extra = "allow"
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }