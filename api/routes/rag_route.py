# api/routes/rag_route.py
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from services.rag import rag_answer
from services.embeddings_index import FaissIndexManager
import os

router = APIRouter(prefix="/rag", tags=["RAG"])

def get_latest_video_id():
    base_dir = "faiss_index"
    if not os.path.exists(base_dir):
        return None
    subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    if not subdirs:
        return None
    subdirs = sorted(subdirs, key=lambda d: os.path.getmtime(os.path.join(base_dir, d)))
    return subdirs[-1]

@router.get("/ask")
def ask_question(q: str = Query(...), video_id: Optional[str] = Query(None)):
    try:
        if not video_id:
            video_id = get_latest_video_id()
            if not video_id:
                raise HTTPException(status_code=404, detail="No FAISS index found")
        response = rag_answer(video_id=video_id, question=q)
        return {"video_id": video_id, "question": q, "answer": response.get("answer"), "sources": response.get("sources", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
def ask_question_post(payload: dict):
    question = payload.get("question")
    video_id = payload.get("video_id")
    if not question:
        raise HTTPException(status_code=400, detail="Missing 'question'")
    try:
        if not video_id:
            video_id = get_latest_video_id()
            if not video_id:
                raise HTTPException(status_code=404, detail="No FAISS index found")
        response = rag_answer(video_id=video_id, question=question)
        return {"video_id": video_id, "question": question, "answer": response.get("answer"), "sources": response.get("sources", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
