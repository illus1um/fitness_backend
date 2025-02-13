from typing import Optional

from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, pattern="^[a-zA-Z0-9_.-]+$")
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=32)


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    role: str

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str
