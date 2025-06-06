from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models.email_verification import EmailVerificationCode

CODE_EXPIRATION_MINUTES = 10

def create_code(db: Session, email: str, code: str):
    record = EmailVerificationCode(email=email, code=code)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_latest_code(db: Session, email: str):
    return db.query(EmailVerificationCode)\
             .filter(EmailVerificationCode.email == email)\
             .order_by(EmailVerificationCode.created_at.desc())\
             .first()

def mark_code_as_used(db: Session, code_obj: EmailVerificationCode):
    code_obj.is_used = True
    db.commit()

def is_code_valid(code_obj: EmailVerificationCode, input_code: str):
    if code_obj.is_used:
        return False
    if code_obj.code != input_code:
        return False
    if datetime.utcnow() - code_obj.created_at > timedelta(minutes=CODE_EXPIRATION_MINUTES):
        return False
    return True
