import random
import logging
from fastapi import FastAPI, HTTPException, status, Depends, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

# 🔹 Внутренние модули проекта
from auth.jwt import create_access_token, create_refresh_token
from auth.dependencies import get_current_user
from database.session import get_db, Base, engine
from schemas.user import UserCreate, UserOut, Token, RefreshTokenRequest
from crud.user import (
    create_user, get_user, get_user_by_email, update_user_password, authenticate_user,
    blacklist_token, save_reset_code, verify_reset_code
)
from models.user import User
from utils.email import send_email

# 🔹 Инициализация FastAPI
app = FastAPI()

# 🔹 Конфигурация логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔹 CORS (разрешаем доступ с фронтенда)
origins = ["http://localhost", "http://10.0.2.2:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 OAuth2 схема для авторизации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 🔹 Создание базы данных (если ещё не создана)
Base.metadata.create_all(bind=engine)


# ============================================================
# 🔹 1️⃣ АУТЕНТИФИКАЦИЯ И АВТОРИЗАЦИЯ
# ============================================================

@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    if get_user(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = create_user(
        db,
        user.username,
        user.email,
        user.password,
        user.first_name,
        user.last_name,
        user.gender
    )
    return new_user


@app.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Вход в систему и выдача токена"""
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
    """Обновление токена"""
    return {
        "access_token": create_access_token({"sub": "username"}),
        "refresh_token": create_refresh_token({"sub": "username"}),
        "token_type": "bearer"
    }


@app.get("/users/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return current_user


@app.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Выход из системы (блокировка токена)"""
    blacklist_token(db, token)
    logger.info(f"Токен заблокирован: {token[:10]}...")
    return {"message": "Вы вышли из системы"}


# ============================================================
# 🔹 2️⃣ ВОССТАНОВЛЕНИЕ ПАРОЛЯ
# ============================================================

@app.post("/forgot-password")
async def forgot_password(email: str = Form(...), db: Session = Depends(get_db)):
    """Запрос на сброс пароля (отправка кода на email)"""
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    reset_code = generate_reset_code()
    save_reset_code(db, email, reset_code)  # Сохраняем код в базе

    email_body = f"""
    <h3>Сброс пароля</h3>
    <p>Ваш код для сброса пароля: <b>{reset_code}</b></p>
    <p>Введите этот код в приложении, чтобы установить новый пароль.</p>
    """

    await send_email(email, "Восстановление пароля", email_body)

    return {"message": "Код сброса пароля отправлен на ваш email"}


@app.post("/verify-reset-code")
def verify_reset(email: str = Form(...), code: str = Form(...), db: Session = Depends(get_db)):
    """Проверка кода сброса пароля"""
    if verify_reset_code(db, email, code):
        return {"message": "Код подтвержден"}
    else:
        raise HTTPException(status_code=400, detail="Неверный или просроченный код")


@app.post("/reset-password")
def reset_password(email: str = Form(...), code: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    """Сброс пароля после успешной проверки кода"""
    if not verify_reset_code(db, email, code):
        raise HTTPException(status_code=400, detail="Неверный или просроченный код")

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    update_user_password(db, user, new_password)

    return {"message": "Пароль успешно изменен"}


# ============================================================
# 🔹 3️⃣ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def generate_reset_code():
    """Генерация случайного 6-значного кода"""
    return str(random.randint(100000, 999999))
