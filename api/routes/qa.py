# api/routes/qa.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from services.rag import rag_answer

router = APIRouter(prefix="/qa", tags=["QA"])

class QAIn(BaseModel):
    video_id: str
    question: str
    k: int = 4

@router.post("/")
def ask_qa(payload: QAIn):
    try:
        res = rag_answer(payload.video_id, payload.question, k=payload.k)
        return res
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Index or transcript not found for provided video_id")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
