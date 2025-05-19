from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from models.water import WaterIntake, WaterIntakeRecord
from schemas.water import WaterIntakeCreate, WaterIntakeRecordCreate


def get_daily_water_intake(db: Session, user_id: int, date: str):
    """Get the total water intake for a specific date"""
    return db.query(WaterIntake).filter(
        and_(WaterIntake.user_id == user_id, WaterIntake.date == date)
    ).first()


def get_water_intake_history(db: Session, user_id: int, limit: int = 30):
    """Get water intake history for a user, limited to the specified number of days"""
    return db.query(WaterIntake).filter(
        WaterIntake.user_id == user_id
    ).order_by(WaterIntake.date.desc()).limit(limit).all()


def get_daily_water_records(db: Session, user_id: int, date: str):
    """Get all water intake records for a specific date"""
    return db.query(WaterIntakeRecord).filter(
        and_(WaterIntakeRecord.user_id == user_id, WaterIntakeRecord.date == date)
    ).order_by(WaterIntakeRecord.timestamp.desc()).all()


def create_water_intake(db: Session, user_id: int, water_intake: WaterIntakeCreate):
    """Create or update daily water intake total"""
    # Check if there's already an entry for this date
    date = water_intake.date
    db_water_intake = get_daily_water_intake(db, user_id, date)

    if db_water_intake:
        # Update existing record
        db_water_intake.amount = water_intake.amount
        db_water_intake.timestamp = datetime.utcnow()
    else:
        # Create new record
        db_water_intake = WaterIntake(
            user_id=user_id,
            date=date,
            amount=water_intake.amount
        )
        db.add(db_water_intake)

    db.commit()
    db.refresh(db_water_intake)
    return db_water_intake


def add_water_intake_record(db: Session, user_id: int, date: str, record: WaterIntakeRecordCreate):
    """Add a single water intake record"""
    db_record = WaterIntakeRecord(
        user_id=user_id,
        date=date,
        amount=record.amount,
        timestamp=record.timestamp
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def update_water_intake(db: Session, user_id: int, date: str, amount: float):
    """Update daily water intake total only"""
    db_water_intake = get_daily_water_intake(db, user_id, date)

    if db_water_intake:
        db_water_intake.amount = amount
        db_water_intake.timestamp = datetime.utcnow()
    else:
        db_water_intake = WaterIntake(
            user_id=user_id,
            date=date,
            amount=amount
        )
        db.add(db_water_intake)

    db.commit()
    db.refresh(db_water_intake)
    return db_water_intake


def delete_day_records(db: Session, user_id: int, date: str):
    """Delete all records for a specific day"""
    db.query(WaterIntakeRecord).filter(
        and_(WaterIntakeRecord.user_id == user_id, WaterIntakeRecord.date == date)
    ).delete()
    db.commit()


def delete_water_intake_record(db: Session, record_id: int, user_id: int):
    """Delete a specific water intake record"""
    db_record = db.query(WaterIntakeRecord).filter(
        and_(WaterIntakeRecord.id == record_id, WaterIntakeRecord.user_id == user_id)
    ).first()

    if db_record:
        db.delete(db_record)
        db.commit()
        return True
    return False


def delete_all_water_data(db: Session, user_id: int):
    """Delete all water intake data for a user"""
    db.query(WaterIntakeRecord).filter(WaterIntakeRecord.user_id == user_id).delete()
    db.query(WaterIntake).filter(WaterIntake.user_id == user_id).delete()
    db.commit()