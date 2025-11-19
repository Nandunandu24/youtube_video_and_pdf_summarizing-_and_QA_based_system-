# api/routes/auth_route.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db
from .. import crud, schemas, auth as auth_utils
from ..services.emailer import send_email
import os

router = APIRouter(prefix="/auth", tags=["auth"])

FRONTEND_BASE = os.environ.get("FRONTEND_BASE", "http://localhost:5173")  # for reset link

@router.post("/signup", response_model=schemas.UserOut)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud.create_user(db, user_in)
    # optional welcome email
    try:
        subject = "Welcome to SummarAI"
        body = f"Hi,\n\nThanks for signing up for SummarAI ({user.email}).\n\n"
        send_email(user.email, subject, body)
    except Exception:
        # do not fail signup if email fails
        pass
    return user

@router.post("/login")
def login(payload: schemas.LoginIn, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, payload.email)
    if not user or not crud.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = auth_utils.create_access_token({"sub": user.email, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer", "user": {"id": user.id, "email": user.email}}

@router.post("/forgot")
def forgot(payload: schemas.ForgotIn, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, payload.email)
    if not user:
        # don't reveal whether email exists
        return {"status": "ok"}
    token = auth_utils.create_access_token({"sub": user.email, "user_id": user.id}, expires_delta=timedelta(minutes=30))
    reset_url = f"{FRONTEND_BASE}/reset-password?token={token}"
    try:
        send_email(user.email, "Reset your SummarAI password", f"Click this link to reset your password:\n\n{reset_url}\n\nThis link will expire in 30 minutes.")
    except Exception as e:
        # email failed — log and continue
        print("Email send failed:", e)
    return {"status": "ok"}

@router.post("/reset")
def reset(payload: schemas.ResetIn, db: Session = Depends(get_db)):
    # validate passwords match
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    # decode token
    try:
        data = auth_utils.decode_access_token(payload.token)
    except HTTPException as e:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    email = data.get("sub")
    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # update password
    crud.update_user_password(db, user, payload.password)
    return {"status": "ok"}
