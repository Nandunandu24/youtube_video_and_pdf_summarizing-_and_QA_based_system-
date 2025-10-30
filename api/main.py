# api/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from .db import init_db, SessionLocal, get_db
from . import models, schemas, crud, auth

app = FastAPI(title="AI Note Summarizer - API")

# run once at startup to create tables (dev only)
@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"status": "ok", "project": "AI Note Summarizer"}

@app.post("/signup", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def signup(user_in: schemas.UserCreate, db=Depends(get_db)):
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db, user_in)
    return user
