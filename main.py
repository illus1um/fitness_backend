from fastapi import FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth.jwt import create_access_token, create_refresh_token
from database.session import get_db
from database.session import Base, engine
from schemas.user import UserCreate, UserOut, Token, RefreshTokenRequest
from crud.user import create_user, get_user, blacklist_token
from models.user import User
from auth.dependencies import get_current_user
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter.depends import RateLimiter
from crud.user import authenticate_user
import logging

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db, user.username, user.email, user.password)

@app.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Неудачная попытка входа: {form_data.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учетные данные")

    logger.info(f"Пользователь {user.username} вошел в систему")
    return {
        "access_token": create_access_token({"sub": user.username}),
        "refresh_token": create_refresh_token({"sub": user.username}),
        "token_type": "bearer"
    }
@app.post("/refresh", response_model=Token)
def refresh_token(refresh_request: RefreshTokenRequest):
    return {"access_token": create_access_token({"sub": "username"}), "refresh_token": create_refresh_token({"sub": "username"}), "token_type": "bearer"}

@app.get("/users/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user  # Должен быть полноценный объект User

@app.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    blacklist_token(db, token)
    logger.info(f"Токен заблокирован: {token[:10]}...")
    return {"message": "Вы вышли из системы"}
