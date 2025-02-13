import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Получаем данные из .env
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# Проверяем, загружены ли ключевые переменные (чтобы избежать ошибок)
if not all([DATABASE_URL, SECRET_KEY]):
    raise ValueError("Не удалось загрузить переменные окружения. Проверь .env файл.")
