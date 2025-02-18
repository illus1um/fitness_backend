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


SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")
RESET_PASSWORD_URL = os.getenv("RESET_PASSWORD_URL")

# Проверяем, загружены ли ключевые переменные (чтобы избежать ошибок)
if not all([DATABASE_URL, SECRET_KEY]):
    raise ValueError("Не удалось загрузить переменные окружения. Проверь .env файл.")
