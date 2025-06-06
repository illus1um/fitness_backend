from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random

from database.session import get_db
import crud.email_verification as crud
from schemas.email_verification import EmailRequest, CodeVerifyRequest
from utils.email import send_email

router = APIRouter()


@router.post("/verify-email/send")
async def send_email_verification(req: EmailRequest, db: Session = Depends(get_db)):
    code = str(random.randint(100000, 999999))
    crud.create_code(db, email=req.email, code=code)

    subject = "Your Verification Code"
    body = f"Your verification code is: {code}"

    success = await send_email(to_email=req.email, subject=subject, body=body)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send verification email")

    return {"message": "Verification code sent"}

@router.post("/verify-email/verify")
def verify_email_code(req: CodeVerifyRequest, db: Session = Depends(get_db)):
    code_obj = crud.get_latest_code(db, email=req.email)
    if not code_obj or not crud.is_code_valid(code_obj, req.code):
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    crud.mark_code_as_used(db, code_obj)
    return {"message": "Email verified successfully"}
