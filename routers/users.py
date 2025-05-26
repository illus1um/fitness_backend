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
from crud.plan import delete_user_plan
import logging
import os
import uuid
import io
from PIL import Image
from fastapi import UploadFile, File

users_router = APIRouter()
logger = logging.getLogger(__name__)

AVATAR_DIR = "media/avatars"
if not os.path.exists(AVATAR_DIR):
    os.makedirs(AVATAR_DIR)

@users_router.get("/me", response_model=UserOut)
def read_users_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="The user was not found")

    return user


@users_router.post("/update-profile")
def update_profile(
        user_data: UserProfileUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="The user was not found")

    should_reset_plan = False

    if user_data.training_program is not None and user.training_program != user_data.training_program:
        should_reset_plan = True
        logger.info(
            f"User {user.id}: training program changed from '{user.training_program}' to '{user_data.training_program}'")

    if user_data.training_location is not None and user.training_location != user_data.training_location:
        should_reset_plan = True
        logger.info(
            f"User {user.id}: training location changed from '{user.training_location}' to '{user_data.training_location}'")

    if user_data.training_experience is not None and user.training_experience != user_data.training_experience:
        should_reset_plan = True
        logger.info(
            f"User {user.id}: training experience changed from '{user.training_experience}' to '{user_data.training_experience}'")

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

    if should_reset_plan:
        logger.info(f"User {user.id}: resetting workout plan due to profile changes")
        delete_user_plan(db, current_user.id)

    db.commit()
    db.refresh(user)

    return {"message": "Profile has been successfully updated", "user": user}


@users_router.get("/profile-status")
def profile_status(current_user: User = Depends(get_current_user)):
    """Checks whether the profile needs to be filled out."""
    if current_user.weight is None or current_user.height is None or current_user.age is None:
        return {"profile_completed": False}

    return {"profile_completed": True}


@users_router.post("/set-program")
def set_training_program(program_data: TrainingProgramUpdate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    """Saving the training program"""
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.training_program != program_data.training_program:
        logger.info(
            f"User {user.id}: training program changed from '{user.training_program}' to '{program_data.training_program}'")
        delete_user_plan(db, current_user.id)

    user.training_program = program_data.training_program
    db.commit()
    db.refresh(user)

    return {"message": "The training program has been updated", "training_program": user.training_program}


@users_router.post("/set-location")
def set_training_location(location_data: TrainingLocationUpdate, db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    """Saving the training place (Home / Gym)"""
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="The user was not found")

    if user.training_location != location_data.training_location:
        logger.info(
            f"User {user.id}: training location changed from '{user.training_location}' to '{location_data.training_location}'")
        delete_user_plan(db, current_user.id)

    user.training_location = location_data.training_location
    db.commit()
    db.refresh(user)

    return {"message": "The training location has been updated", "training_location": user.training_location}


@users_router.post("/set-experience")
def set_training_experience(experience_data: TrainingExperienceUpdate, db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    """Saving training experience"""
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="The user was not found")

    if user.training_experience != experience_data.training_experience:
        logger.info(
            f"User {user.id}: training experience changed from '{user.training_experience}' to '{experience_data.training_experience}'")
        delete_user_plan(db, current_user.id)

    user.training_experience = experience_data.training_experience
    db.commit()
    db.refresh(user)

    return {"message": "The training level has been updated", "training_experience": user.training_experience}


@users_router.post("/update-training-program")
def update_training_program(
        data: TrainingProgramUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if user and user.training_program != data.training_program:
        delete_user_plan(db, current_user.id)

    update_training_program(db, current_user, data.training_program)
    return {"message": "The training plan has been successfully updated"}


@users_router.post("/update-training-location")
def update_training_location(
        data: TrainingLocationUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if user and user.training_location != data.training_location:
        delete_user_plan(db, current_user.id)

    update_training_location(db, current_user, data.training_location)
    return {"message": "The training location has been successfully updated"}


@users_router.post("/update-training-experience")
def update_training_experience(
        data: TrainingExperienceUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if user and user.training_experience != data.training_experience:
        delete_user_plan(db, current_user.id)

    update_training_experience(db, current_user, data.training_experience)
    return {"message": "The training level has been successfully updated"}


@users_router.delete("/delete-account")
def delete_account(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Deleting the current user's account"""
    if not current_user:
        raise HTTPException(status_code=404, detail="The user was not found")

    if current_user.avatar_url:
        file_path = os.path.join(".", current_user.avatar_url.lstrip("/"))
        if os.path.exists(file_path):
            os.remove(file_path)

    delete_user(db, current_user)

    return {"message": "Account successfully deleted"}


@users_router.post("/change-password")
def change_password(
        request: ChangePasswordRequest,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Changes the user's password"""
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    update_user_password(db, current_user, request.new_password)
    return {"message": "Password updated successfully"}


@users_router.post("/upload-avatar")
async def upload_avatar(
        avatar: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Uploads the user's avatar"""

    allowed_formats = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if avatar.content_type not in allowed_formats:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG and WebP images are allowed")

    file_extension = avatar.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(AVATAR_DIR, unique_filename)

    contents = await avatar.read()
    
    try:
        img = Image.open(io.BytesIO(contents))
        
        max_size = (800, 800)
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.LANCZOS)
        
        img.save(file_path, optimize=True, quality=85)
    except Exception as e:
        logger.error(f"Error optimizing avatar for user {current_user.id}: {str(e)}")
        with open(file_path, "wb") as f:
            f.write(contents)

    avatar_url = f"/media/avatars/{unique_filename}"

    user = db.query(User).filter(User.id == current_user.id).first()

    if user.avatar_url:
        old_avatar_path = os.path.join(".", user.avatar_url.lstrip("/"))
        if os.path.exists(old_avatar_path):
            os.remove(old_avatar_path)

    user.avatar_url = avatar_url
    db.commit()

    return {"avatar_url": avatar_url}


@users_router.delete("/delete-avatar")
async def delete_avatar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletes the user's avatar"""
    user = db.query(User).filter(User.id == current_user.id).first()
    
    if user.avatar_url:
        file_path = os.path.join(".", user.avatar_url.lstrip("/"))
        if os.path.exists(file_path):
            os.remove(file_path)
        
        user.avatar_url = None
        db.commit()
        return {"message": "Avatar removed"}
    
    raise HTTPException(status_code=404, detail="Avatar not found")