from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from schemas.user import UserOut, UserUpdate
from models.user import User
from auth.dependencies import get_current_user
from schemas.user import TrainingProgramUpdate
from schemas.user import TrainingLocationUpdate
from schemas.user import TrainingExperienceUpdate


users_router = APIRouter()

@users_router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return current_user

@users_router.post("/update-profile")
def update_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user_data.weight:
        user.weight = user_data.weight
    if user_data.height:
        user.height = user_data.height
    if user_data.age:
        user.age = user_data.age

    db.commit()
    db.refresh(user)

    return {"message": "Профиль успешно обновлен", "user": user}

@users_router.get("/profile-status")
def profile_status(current_user: User = Depends(get_current_user)):
    """Проверяет, нужно ли заполнять профиль"""
    if current_user.weight is None or current_user.height is None or current_user.age is None:
        return {"profile_completed": False}  # Нужно заполнить

    return {"profile_completed": True}  # Профиль уже заполнен

@users_router.post("/set-program")
def set_training_program(program_data: TrainingProgramUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Сохраняем программу тренировок"""
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.training_program = program_data.training_program
    db.commit()
    db.refresh(user)

    return {"message": "Программа тренировок обновлена", "training_program": user.training_program}

@users_router.post("/set-location")
def set_training_location(location_data: TrainingLocationUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Сохраняем место тренировки (Дом / Зал)"""
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.training_location = location_data.training_location
    db.commit()
    db.refresh(user)

    return {"message": "Место тренировки обновлено", "training_location": user.training_location}

@users_router.post("/set-experience")
def set_training_experience(experience_data: TrainingExperienceUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Сохраняем уровень подготовки"""
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.training_experience = experience_data.training_experience
    db.commit()
    db.refresh(user)

    return {"message": "Уровень подготовки обновлен", "training_experience": user.training_experience}