from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth.jwt import create_access_token, create_refresh_token
from database.session import get_db
from schemas.user import Token, RefreshTokenRequest
from crud.user import authenticate_user, blacklist_token, get_user_by_email
import logging
from crud.user import create_user, get_user
from schemas.user import UserCreate, UserOut

auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

logger = logging.getLogger(__name__)


@auth_router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")

    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    return create_user(db, user.username, user.email, user.password, user.first_name, user.last_name, user.gender)


@auth_router.get("/check-username")
def check_username(username: str, db: Session = Depends(get_db)):
    if get_user(db, username):
        raise HTTPException(status_code=400, detail="Username already taken")
    return {"available": True}


@auth_router.get("/check-email")
def check_email(email: str, db: Session = Depends(get_db)):
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already taken")
    return {"available": True}


@auth_router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt: {form_data.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    logger.info(f"User {user.username} logged in")
    return {
        "access_token": create_access_token({"sub": user.username}),
        "refresh_token": create_refresh_token({"sub": user.username}),
        "token_type": "bearer"
    }


@auth_router.post("/refresh", response_model=Token)
def refresh_token(refresh_request: RefreshTokenRequest):
    return {
        "access_token": create_access_token({"sub": "username"}),
        "refresh_token": create_refresh_token({"sub": "username"}),
        "token_type": "bearer"
    }


@auth_router.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    blacklist_token(db, token)
    logger.info(f"Token blacklisted: {token[:10]}...")
    return {"message": "You have been logged out"}
