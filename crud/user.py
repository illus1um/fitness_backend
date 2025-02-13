from sqlalchemy.orm import Session
from models.user import User
from auth.hashing import get_password_hash
from auth.hashing import verify_password
from models.user import BlacklistedToken

def create_user(db: Session, username: str, email: str, password: str):
    hashed_password = get_password_hash(password)
    db_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    """Проверяет, существует ли пользователь и правильный ли у него пароль"""
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def blacklist_token(db: Session, token: str):
    db_token = BlacklistedToken(token=token)
    db.add(db_token)
    db.commit()

def is_token_blacklisted(db: Session, token: str) -> bool:
    return db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first() is not None