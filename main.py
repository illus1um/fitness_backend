from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth.jwt import create_access_token, create_refresh_token
from auth.hashing import verify_password
from database.session import get_db
from database.session import Base, engine
from schemas.user import UserCreate, UserOut, Token, RefreshTokenRequest
from crud.user import create_user, get_user
from models.user import User
from auth.dependencies import get_current_user


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

Base.metadata.create_all(bind=engine)

@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db, user.username, user.email, user.password)

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

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
