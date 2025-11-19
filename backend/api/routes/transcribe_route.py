# routes/transcribe_route.py
from fastapi import APIRouter, HTTPException
from services.transcribe import transcribe_and_index

router = APIRouter(prefix="/process", tags=["Transcription & Indexing"])

@router.post("/")
def process_video(youtube_url: str):
    try:
        result = transcribe_and_index(youtube_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

