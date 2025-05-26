from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database.session import get_db
from schemas.progress import ProgressEntry, ProgressCreate
from crud.progress import get_progress, get_day_progress, upsert_progress, delete_all_user_progress

router = APIRouter(tags=["Progress"])

@router.get("/", response_model=List[ProgressEntry])
def read_progress(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_progress(db, current_user.id)

@router.get("/{day_index}", response_model=List[ProgressEntry])
def read_day_progress(
    day_index: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_day_progress(db, current_user.id, day_index)

@router.post("/", response_model=ProgressEntry)
def create_or_update_progress(
    progress_data: ProgressCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return upsert_progress(db, current_user.id, progress_data)

@router.delete("/", response_model=Dict[str, str])
def clear_user_progress(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Deletes the entire training progress of the current user."""
    delete_all_user_progress(db, current_user.id)
    return {"status": "success", "message": "All progress has been deleted"}