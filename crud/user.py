from sqlalchemy.orm import Session
from models.user import User
from auth.hashing import get_password_hash
from auth.hashing import verify_password
from models.user import BlacklistedToken
import datetime

def create_user(db: Session, username: str, email: str, password: str, first_name: str, last_name: str, gender: bool):
    hashed_password = get_password_hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        gender=gender
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def blacklist_token(db: Session, token: str):
    existing_token = db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first()
    if existing_token:
        return

    db_token = BlacklistedToken(token=token, created_at=datetime.datetime.utcnow())
    db.add(db_token)
    db.commit()

def is_token_blacklisted(db: Session, token: str) -> bool:
    return db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first() is not None

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def update_user_password(db: Session, user: User, new_password: str):
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)

reset_codes = {}

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def update_user_password(db: Session, user: User, new_password: str):
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)

def save_reset_code(db: Session, email: str, code: str):
    reset_codes[email] = {"code": code, "expires_at": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)}

def verify_reset_code(db: Session, email: str, code: str):
    if email in reset_codes:
        stored_code = reset_codes[email]
        if stored_code["code"] == code and stored_code["expires_at"] > datetime.datetime.utcnow():
            return True
    return False

def update_training_program(db: Session, user: User, training_program: str):
    user.training_program = training_program
    db.commit()
    db.refresh(user)

def update_training_location(db: Session, user: User, training_location: str):
    user.training_location = training_location
    db.commit()
    db.refresh(user)

def update_training_experience(db: Session, user: User, training_experience: str):
    user.training_experience = training_experience
    db.commit()
    db.refresh(user)

def delete_user(db: Session, user: User):
    db.delete(user)
    db.commit()
