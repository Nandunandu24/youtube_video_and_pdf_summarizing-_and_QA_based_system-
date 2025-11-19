# api/routes/summarize_route.py
from fastapi import APIRouter, HTTPException
from services.summarize import generate_summary_json
import os

router = APIRouter(prefix="/summarize", tags=["Summarize"])

@router.get("/{video_id}")
def summarize_video(video_id: str):
    try:
        # Will raise FileNotFoundError if meta not found
        summary = generate_summary_json(video_id)
        return summary
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
