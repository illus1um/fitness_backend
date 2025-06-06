import random
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from crud.user import get_user_by_email, update_user_password, save_reset_code, verify_reset_code
from utils.email import send_email

password_reset_router = APIRouter()

@password_reset_router.post("/forgot")
async def forgot_password(email: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="The user was not found")

    reset_code = str(random.randint(100000, 999999))
    save_reset_code(db, email, reset_code)

    email_body = f"Your password reset code: {reset_code}"
    await send_email(email, "Password Recovery", email_body)

    return {"message": "The code has been sent"}

@password_reset_router.post("/verify")
def verify_reset(email: str = Form(...), code: str = Form(...), db: Session = Depends(get_db)):
    if verify_reset_code(db, email, code):
        return {"message": "The code is confirmed"}
    raise HTTPException(status_code=400, detail="Invalid code")

@password_reset_router.post("/reset")
def reset_password(email: str = Form(...), code: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    if not verify_reset_code(db, email, code):
        raise HTTPException(status_code=400, detail="Invalid code")

    update_user_password(db, get_user_by_email(db, email), new_password)
    return {"message": "The password has been changed"}
