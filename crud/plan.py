from sqlalchemy.orm import Session
from models.plan import Plan
from schemas.plan import PlanCreate
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def get_user_plan(db: Session, user_id: int) -> Plan:
    """Gets the user's training plan"""
    try:
        plan = db.query(Plan).filter(Plan.user_id == user_id).first()
        if plan:
            logger.info(f"Found plan for user {user_id}")
        else:
            logger.info(f"No plan found for user {user_id}")
        return plan
    except Exception as e:
        logger.error(f"Error getting plan for user {user_id}: {str(e)}")
        raise


def save_plan(db: Session, user_id: int, plan: PlanCreate) -> Plan:
    """Saves or updates the user's training plan"""
    try:
        db_plan = get_user_plan(db, user_id)

        # Save days and exercises as is without transformation
        days_data = [day.dict(exclude_unset=True) for day in plan.days]

        if db_plan:
            logger.info(f"Updating existing plan for user {user_id}")
            db_plan.start_date = plan.start_date
            db_plan.days = days_data
        else:
            logger.info(f"Creating new plan for user {user_id}")
            db_plan = Plan(
                user_id=user_id,
                start_date=plan.start_date,
                days=days_data
            )
            db.add(db_plan)

        db.commit()
        db.refresh(db_plan)
        logger.info(f"Plan saved successfully for user {user_id}")
        return db_plan

    except Exception as e:
        logger.error(f"Error saving plan for user {user_id}: {str(e)}")
        db.rollback()
        raise


def delete_user_plan(db: Session, user_id: int) -> None:
    """Deletes the user's training plan"""
    try:
        db.query(Plan).filter(Plan.user_id == user_id).delete()
        db.commit()
        logger.info(f"Plan deleted for user {user_id}")
    except Exception as e:
        logger.error(f"Error deleting plan for user {user_id}: {str(e)}")
        db.rollback()
        raise