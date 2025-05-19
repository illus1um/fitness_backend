from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database.session import get_db
from crud import water as water_crud
from models.user import User
from schemas.water import (
    WaterIntake,
    WaterIntakeCreate,
    WaterIntakeRequest,
    WaterIntakeHistoryResponse,
    DailyWaterIntakeResponse,
    WaterIntakeRecord,
    WaterIntakeRecordCreate
)

router = APIRouter(tags=["Water Tracking"])


@router.get("/history", response_model=List[WaterIntake])
def get_water_history(
        limit: int = Query(30, description="Number of days to retrieve"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get water intake history for the current user"""
    history = water_crud.get_water_intake_history(db, current_user.id, limit)
    return history


@router.get("/daily/{date}", response_model=DailyWaterIntakeResponse)
def get_daily_water_intake(
        date: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get water intake records for a specific date"""
    intake = water_crud.get_daily_water_intake(db, current_user.id, date)
    if not intake:
        # Return empty response if no data
        return {"date": date, "total_amount": 0.0, "records": []}

    records = water_crud.get_daily_water_records(db, current_user.id, date)
    return {
        "date": date,
        "total_amount": intake.amount,
        "records": records
    }


@router.post("/add", response_model=WaterIntake)
def add_water_intake(
        request: WaterIntakeRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Add water intake for the current date.
    Optionally include detailed records with timestamps.
    """
    # Get current date in YYYY-MM-DD format
    today = datetime.now().strftime("%Y-%m-%d")

    # Create or update daily total
    water_intake = WaterIntakeCreate(date=today, amount=request.amount)
    result = water_crud.create_water_intake(db, current_user.id, water_intake)

    # Add detailed records if provided
    if request.records:
        for record in request.records:
            water_crud.add_water_intake_record(db, current_user.id, today, record)
    # If no records provided, add one record with the total amount
    elif request.amount > 0:
        record = WaterIntakeRecordCreate(
            amount=request.amount,
            timestamp=datetime.now()
        )
        water_crud.add_water_intake_record(db, current_user.id, today, record)

    return result


@router.post("/records", response_model=WaterIntakeRecord)
def add_water_record(
        record: WaterIntakeRecordCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Add a single water intake record for the current date"""
    today = datetime.now().strftime("%Y-%m-%d")

    # Add the record
    db_record = water_crud.add_water_intake_record(db, current_user.id, today, record)

    # Update the daily total
    existing_intake = water_crud.get_daily_water_intake(db, current_user.id, today)
    if existing_intake:
        new_amount = existing_intake.amount + record.amount
    else:
        new_amount = record.amount

    water_crud.update_water_intake(db, current_user.id, today, new_amount)

    return db_record


@router.delete("/records/{record_id}")
def delete_water_record(
        record_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Delete a specific water intake record and update the daily total"""
    # Get the record to be deleted
    record = db.query(WaterIntakeRecord).filter_by(id=record_id, user_id=current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # Keep track of the date and amount
    date = record.date
    amount_to_deduct = record.amount

    # Delete the record
    success = water_crud.delete_water_intake_record(db, record_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Record not found")

    # Update the daily total
    daily_intake = water_crud.get_daily_water_intake(db, current_user.id, date)
    if daily_intake:
        new_amount = max(0, daily_intake.amount - amount_to_deduct)
        water_crud.update_water_intake(db, current_user.id, date, new_amount)

    return {"message": "Record deleted successfully"}


@router.delete("/daily/{date}")
def delete_day_water_intake(
        date: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Delete all water intake records for a specific date"""
    # First delete all records
    water_crud.delete_day_records(db, current_user.id, date)

    # Then set the daily total to 0
    water_crud.update_water_intake(db, current_user.id, date, 0)

    return {"message": f"All water intake data for {date} deleted"}


@router.delete("/all")
def delete_all_water_data(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Delete all water intake data for the current user"""
    water_crud.delete_all_water_data(db, current_user.id)
    return {"message": "All water intake data deleted"}