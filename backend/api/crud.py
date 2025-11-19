# api/crud.py
from sqlalchemy.orm import Session
from . import models
from .schemas import UserCreate
from passlib.context import CryptContext
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MAX_PW_BYTES = 72

def hash_password(password: str) -> str:
    pw = password.strip()
    if len(pw.encode("utf-8")) > MAX_PW_BYTES:
        pw = pw[:MAX_PW_BYTES]
    return pwd_context.hash(pw)

def verify_password(plain: str, hashed: str) -> bool:
    try:
        pw = plain.strip()
        if len(pw.encode("utf-8")) > MAX_PW_BYTES:
            pw = pw[:MAX_PW_BYTES]
        return pwd_context.verify(pw, hashed)
    except Exception:
        return False

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user_in: UserCreate):
    if user_in.password != user_in.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    if len(user_in.password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password too short (min 8 chars)")
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(user_in.password)
    user = models.User(email=user_in.email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user_password(db: Session, user: models.User, new_password: str):
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password too short (min 8 chars)")
    hashed = hash_password(new_password)
    user.hashed_password = hashed
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
