# api/routes/process.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.audio_download import download_audio
from services.transcribe import transcribe_audio_file
from services.chunking import chunk_transcript_segments
from services.embeddings_index import FaissIndexManager

router = APIRouter(prefix="/process", tags=["Process"])

class ProcessIn(BaseModel):
    youtube_url: str
    model_name: str = "small"

@router.post("/")
def process_video(payload: ProcessIn):
    try:
        wav, meta = download_audio(payload.youtube_url)
        transcript_path, transcript_result = transcribe_audio_file(wav, model_name=payload.model_name)
        segments = transcript_result.get("segments", [])
        if not segments:
            return {"status": "error", "detail": "No segments found in transcript."}
        chunks, metadatas = chunk_transcript_segments(segments, chunk_size=1000, chunk_overlap=200)
        manager = FaissIndexManager()
        index_path, meta_path = manager.build_and_save(meta["id"], chunks, metadatas)
        return {"status": "success", "video_id": meta["id"], "transcript": transcript_path, "index": index_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
