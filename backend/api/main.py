# api/main.py
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
import os
from sqlalchemy.orm import Session

# ------------------------
# Internal imports (fixed paths)
# ------------------------
from .db import init_db, get_db
from . import schemas, crud

# Routes inside api/
from .schemas import UserCreate, UserOut, LoginIn


from .routes.auth_route import router as auth_router

from .routes.youtube import router as youtube_router
from .routes.transcribe_route import router as transcribe_router
from .routes.rag_route import router as rag_router
from .routes.summarize_route import router as summarize_router
from .routes.qa import router as qa_router

# Routes outside api/ (files upload)
from .routes.files import router as files_router

# ------------------------
# FAISS + RAG core services
# ------------------------
from services.embeddings_index import FaissIndexManager
from services.rag import rag_answer

# ------------------------
# Initialize App
# ------------------------
app = FastAPI(title="AI Video & Document Summarizer / RAG Engine")

# ------------------------
# CORS
# ------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # change to your frontend domain if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# Startup: Initialize DB
# ------------------------
@app.on_event("startup")
def on_startup():
    try:
        init_db()
        print("✅ Database initialized successfully.")
    except Exception as e:
        print(f"⚠️ Database initialization skipped or failed: {e}")

# ------------------------
# Root endpoint
# ------------------------
@app.get("/")
def root():
    return {"status": "ok", "project": "AI YouTube & Document Summarizer"}

# ------------------------
# User Signup
# ------------------------
@app.post("/signup", response_model=UserOut)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(db, user_in)
    return user

@app.post("/login")
def login(user_in: LoginIn, db: Session = Depends(get_db)):

    user = get_user_by_email(db, user_in.email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")

    return user


# ====================================================
# INCLUDE ROUTERS (clean + fixed order)
# ====================================================
app.include_router(auth_router)           # /auth/*
app.include_router(youtube_router)         # /youtube/*
app.include_router(transcribe_router)      # /process/*
app.include_router(files_router)           # /files/*
app.include_router(rag_router)             # /rag/*
app.include_router(qa_router)              # /qa/*
app.include_router(summarize_router)       # /summarize/*



# ====================================================
# Unified RAG endpoint (text query about video/file)
# ====================================================
@app.get("/rag/query")
def rag_query(
    question: str = Query(..., description="Ask a question about the transcript or document"),
    video_id: str | None = Query(None, description="Optional: Video/File ID")
):
    try:
        fm = FaissIndexManager()

        # If no id, get the most recent FAISS index
        if not video_id:
            video_id = fm._get_latest_video_id()

        if not video_id:
            raise HTTPException(status_code=404, detail="No FAISS index found. Process a video or file first.")

        # Retrieve + answer
        answer_data = rag_answer(video_id, question)

        return {
            "video_id": video_id,
            "question": question,
            "answer": answer_data["answer"],
            "sources": answer_data.get("sources", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG Query Failed: {str(e)}")


@app.post("/rag/query")
def rag_query_post(payload: dict):
    question = payload.get("question")
    video_id = payload.get("video_id")

    if not question:
        raise HTTPException(status_code=400, detail="Missing field: question")

    try:
        fm = FaissIndexManager()

        if not video_id:
            video_id = fm._get_latest_video_id()

        answer_data = rag_answer(video_id, question)

        return {
            "video_id": video_id,
            "question": question,
            "answer": answer_data["answer"],
            "sources": answer_data.get("sources", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG POST Failed: {str(e)}")
