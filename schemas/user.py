from typing import Optional

from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, pattern="^[a-zA-Z0-9_.-]+$")
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=32)
    first_name: str = Field(..., min_length=1, max_length=30)
    last_name: str = Field(..., min_length=1, max_length=30)
    gender: bool  # True = Мужской, False = Женский


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    gender: bool
    is_active: bool
    role: str
    weight: Optional[float] = None
    height: Optional[float] = None
    age: Optional[int] = None
    training_program: Optional[str] = None
    training_location: Optional[str] = None
    training_experience: Optional[str] = None

    class Config:
        orm_mode = True

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[bool] = None  # True = Мужской, False = Женский
    weight: Optional[float] = None
    height: Optional[float] = None
    age: Optional[int] = None
    training_program: Optional[str] = None
    training_location: Optional[str] = None
    training_experience: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
class UserLogin(BaseModel):
    username: str
    password: str

class TrainingProgramUpdate(BaseModel):
    training_program: str = Field(..., min_length=3, max_length=50)

class TrainingLocationUpdate(BaseModel):
    training_location: str = Field(..., min_length=3, max_length=20)

class TrainingExperienceUpdate(BaseModel):
    training_experience: str = Field(..., min_length=3, max_length=20)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr