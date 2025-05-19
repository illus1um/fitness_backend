from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database.session import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas.plan import PlanCreate, PlanOut
from crud.plan import get_user_plan, save_plan, delete_user_plan
import logging
import json
from typing import Dict, Any
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Plan"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=PlanOut)
def read_plan(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Получает план тренировок текущего пользователя"""
    try:
        plan = get_user_plan(db, current_user.id)
        if not plan:
            logger.info(f"No plan found for user {current_user.id}")
            raise HTTPException(status_code=404, detail="Plan not found")
        logger.info(f"Plan retrieved successfully for user {current_user.id}")
        return plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving plan for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/", response_model=PlanOut)
async def create_or_update_plan(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Создает или обновляет план тренировок"""
    try:
        # Логируем сырые данные запроса
        body = await request.body()
        raw_data = body.decode()
        logger.info(f"Raw request body: {raw_data}")

        # Пробуем распарсить JSON
        try:
            json_data = json.loads(raw_data)
            logger.info(f"Parsed JSON data: {json.dumps(json_data, indent=2)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={"message": "Invalid JSON format", "error": str(e)}
            )

        # Пробуем создать объект PlanCreate
        try:
            plan = PlanCreate(**json_data)
            logger.info(f"Created plan object successfully")
        except Exception as e:
            logger.error(f"PlanCreate validation error: {str(e)}")
            return JSONResponse(
                status_code=422,
                content={"message": "Invalid plan data", "error": str(e)}
            )

        # Сохраняем план
        try:
            result = save_plan(db, current_user.id, plan)
            logger.info(f"Plan saved successfully for user {current_user.id}")
            return result
        except Exception as e:
            logger.error(f"Error saving plan: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"message": "Error saving plan", "error": str(e)}
            )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "error": str(e)}
        )


@router.delete("/")
def delete_plan(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Удаляет план тренировок пользователя"""
    try:
        delete_user_plan(db, current_user.id)
        logger.info(f"Plan deleted successfully for user {current_user.id}")
        return {"status": "success", "message": "Plan has been deleted"}
    except Exception as e:
        logger.error(f"Error deleting plan for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting plan: {str(e)}"
        )


@router.post("/test")
async def test_plan_data(
        request: Request,
):
    """Тестовый эндпоинт для проверки данных"""
    try:
        # Логируем сырые данные запроса
        body = await request.body()
        raw_data = body.decode()
        logger.info(f"Raw request body: {raw_data}")

        # Пробуем распарсить JSON
        try:
            json_data = json.loads(raw_data)
            logger.info(f"Parsed JSON data: {json.dumps(json_data, indent=2)}")

            # Проверяем структуру данных
            if 'days' in json_data:
                first_day = json_data['days'][0]
                logger.info(f"First day: {json.dumps(first_day, indent=2)}")

                if 'exercises' in first_day:
                    first_exercise = first_day['exercises'][0]
                    logger.info(f"First exercise: {json.dumps(first_exercise, indent=2)}")

            return {
                "message": "Test endpoint successful",
                "data_received": json_data
            }

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return {
                "error": "Invalid JSON format",
                "details": str(e)
            }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "error": "Unexpected error",
            "details": str(e)
        }