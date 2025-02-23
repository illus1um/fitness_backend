from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from schemas.user import UserOut, UserProfileUpdate, ChangePasswordRequest
from models.user import User
from crud.user import delete_user
from auth.dependencies import get_current_user
from schemas.user import TrainingProgramUpdate
from schemas.user import TrainingLocationUpdate
from schemas.user import TrainingExperienceUpdate
from crud.user import update_user_password
from auth.hashing import verify_password

  # Добавляем новую схему

users_router = APIRouter()

@users_router.get("/me", response_model=UserOut)
def read_users_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user

@users_router.post("/update-profile")
def update_profile(
    user_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Обновляем данные пользователя
    if user_data.first_name is not None:
        user.first_name = user_data.first_name
    if user_data.last_name is not None:
        user.last_name = user_data.last_name
    if user_data.gender is not None:
        user.gender = user_data.gender
    if user_data.weight is not None:
        user.weight = user_data.weight
    if user_data.height is not None:
        user.height = user_data.height
    if user_data.age is not None:
        user.age = user_data.age
    if user_data.training_program is not None:
        user.training_program = user_data.training_program
    if user_data.training_location is not None:
        user.training_location = user_data.training_location
    if user_data.training_experience is not None:
        user.training_experience = user_data.training_experience

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

@users_router.post("/update-training-program")
def update_training_program(
    data: TrainingProgramUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_training_program(db, current_user, data.training_program)
    return {"message": "Тренировочный план успешно обновлен"}

@users_router.post("/update-training-location")
def update_training_location(
    data: TrainingLocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_training_location(db, current_user, data.training_location)
    return {"message": "Место тренировок успешно обновлено"}

@users_router.post("/update-training-experience")
def update_training_experience(
    data: TrainingExperienceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_training_experience(db, current_user, data.training_experience)
    return {"message": "Уровень подготовки успешно обновлен"}

@users_router.delete("/delete-account")
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удаление аккаунта текущего пользователя"""
    if not current_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    delete_user(db, current_user)

    return {"message": "Аккаунт успешно удален"}

@users_router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Смена пароля пользователя"""
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    update_user_password(db, current_user, request.new_password)
    return {"message": "Password updated successfully"}