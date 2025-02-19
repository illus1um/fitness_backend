import random
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from crud.user import get_user_by_email, update_user_password, save_reset_code, verify_reset_code
from utils.email import send_email

password_reset_router = APIRouter()

@password_reset_router.post("/forgot")
async def forgot_password(email: str = Form(...), db: Session = Depends(get_db)):
    """Запрос на сброс пароля (отправка кода на email)"""
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    reset_code = str(random.randint(100000, 999999))
    save_reset_code(db, email, reset_code)

    email_body = f"Ваш код для сброса пароля: {reset_code}"
    await send_email(email, "Восстановление пароля", email_body)

    return {"message": "Код отправлен"}

@password_reset_router.post("/verify")
def verify_reset(email: str = Form(...), code: str = Form(...), db: Session = Depends(get_db)):
    """Проверка кода сброса пароля"""
    if verify_reset_code(db, email, code):
        return {"message": "Код подтвержден"}
    raise HTTPException(status_code=400, detail="Неверный код")

@password_reset_router.post("/reset")
def reset_password(email: str = Form(...), code: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    """Сброс пароля"""
    if not verify_reset_code(db, email, code):
        raise HTTPException(status_code=400, detail="Неверный код")

    update_user_password(db, get_user_by_email(db, email), new_password)
    return {"message": "Пароль изменен"}
