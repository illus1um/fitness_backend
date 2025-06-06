from datetime import datetime
from pydantic import BaseModel

class ProgressEntry(BaseModel):
    day_index: int
    exercise_id: str
    sets_completed: int
    completed_at: datetime

    class Config:
        from_attributes = True

class ProgressCreate(BaseModel):
    day_index: int
    exercise_id: str
    sets_completed: int
