import datetime
from sqlalchemy.orm import Session
from models.progress import Progress
from schemas.progress import ProgressCreate


def get_progress(db: Session, user_id: int):
    return db.query(Progress).filter(Progress.user_id == user_id).all()


def get_day_progress(db: Session, user_id: int, day_index: int):
    return (
        db.query(Progress)
        .filter(Progress.user_id == user_id, Progress.day_index == day_index)
        .all()
    )


def upsert_progress(db: Session, user_id: int, entry: ProgressCreate):
    db_entry = (
        db.query(Progress)
        .filter(
            Progress.user_id == user_id,
            Progress.day_index == entry.day_index,
            Progress.exercise_id == entry.exercise_id
        )
        .first()
    )

    if db_entry:
        db_entry.sets_completed = entry.sets_completed
        db_entry.completed_at = datetime.datetime.utcnow()
    else:
        db_entry = Progress(
            user_id=user_id,
            day_index=entry.day_index,
            exercise_id=entry.exercise_id,
            sets_completed=entry.sets_completed,
            completed_at=datetime.datetime.utcnow()
        )
        db.add(db_entry)

    db.commit()
    db.refresh(db_entry)
    return db_entry


def delete_all_user_progress(db: Session, user_id: int):
    """
    Deletes all training progress for the specified user.

    Args:
        db: Database session
        user_id: User ID
    """
    db.query(Progress).filter(Progress.user_id == user_id).delete()
    db.commit()