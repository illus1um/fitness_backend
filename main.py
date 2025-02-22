from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.session import Base, engine
import logging

from routers.auth import auth_router
from routers.users import users_router
from routers.password_reset import password_reset_router

# 🔹 Инициализация FastAPI
app = FastAPI()

# 🔹 Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔹 CORS (разрешаем доступ с фронтенда)
origins = [
    "http://localhost",
    "http://10.0.2.2:8000",
    "http://192.168.1.76:8000",  # ✅ Добавляем IP ноутбука
    "http://192.168.1.76",       # ✅ На случай, если порт не указан
    "*",  # ✅ (для тестов) Разрешает все источники
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Создание таблиц в базе (если ещё не созданы)
Base.metadata.create_all(bind=engine)

# 🔹 Подключаем роутеры
app.include_router(auth_router, prefix="/auth", tags=["Аутентификация"])
app.include_router(users_router, prefix="/users", tags=["Пользователи"])
app.include_router(password_reset_router, prefix="/password", tags=["Восстановление пароля"])
