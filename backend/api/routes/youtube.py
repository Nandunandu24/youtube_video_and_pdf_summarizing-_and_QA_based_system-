# api/routes/youtube.py

from fastapi import APIRouter, HTTPException, Query
from pydantic import HttpUrl
import logging
import os
import json

from services.audio_download import download_audio
from services.transcribe import transcribe_and_index
from services.chunking import chunk_text_from_segments
from services.embeddings_index import FaissIndexManager
from langchain_text_splitters import RecursiveCharacterTextSplitter

# -----------------------------
# THIS ROUTER WAS MISSING
# -----------------------------
router = APIRouter(
    prefix="/youtube",
    tags=["YouTube"]
)

logger = logging.getLogger("youtube_route")


# -----------------------------
# Download audio
# -----------------------------
@router.post("/download")
def download_youtube_audio(youtube_url: HttpUrl = Query(...)):
    try:
        wav_path, metadata = download_audio(str(youtube_url))
        return {"status": "success", "file_path": wav_path, "metadata": metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# FULL PROCESS PIPELINE
# -----------------------------
@router.post("/process")
def process_youtube_video(youtube_url: HttpUrl = Query(...)):
    try:
        result = transcribe_and_index(str(youtube_url))
        video_id = result["video_id"]
        transcript_path = result["transcript_path"]

        # --- Check transcript file ---
        if not os.path.exists(transcript_path):
            raise HTTPException(
                status_code=500,
                detail=f"Transcript file missing: {transcript_path}"
            )

        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript_data = json.load(f)

        segments = transcript_data.get("segments", [])

        # ------------------------------------------
        # CHUNK BUILDING
        # ------------------------------------------
        if segments:
            # Build text chunks
            chunks = chunk_text_from_segments(segments)

            # Timestamp mapping
            full_text = " ".join(seg["text"] for seg in segments)
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=800, chunk_overlap=50
            )
            text_chunks = splitter.split_text(full_text)

            seg_texts = [s["text"] for s in segments]
            seg_starts = [s["start"] for s in segments]
            seg_ends = [s["end"] for s in segments]

            metadatas = []
            seg_ptr = 0

            for chunk in text_chunks:
                chunk = chunk.strip()
                if not chunk:
                    continue

                start_ts, end_ts = None, None
                accum = ""

                for i in range(seg_ptr, len(seg_texts)):
                    if start_ts is None:
                        start_ts = seg_starts[i]
                    end_ts = seg_ends[i]

                    accum += " " + seg_texts[i]
                    if len(accum) >= len(chunk):
                        seg_ptr = i + 1
                        break

                if start_ts is None:
                    start_ts = 0.0
                if end_ts is None:
                    end_ts = start_ts

                metadatas.append({
                    "chunk_text": chunk,
                    "start": float(start_ts),
                    "end": float(end_ts)
                })

        else:
            # Fallback
            full_text = transcript_data.get("text", "")
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=800, chunk_overlap=50
            )
            chunks = splitter.split_text(full_text)

            metadatas = [
                {
                    "chunk_text": chunk,
                    "start": i * 10.0,
                    "end": (i + 1) * 10.0
                }
                for i, chunk in enumerate(chunks)
            ]

        if not chunks:
            raise HTTPException(status_code=500, detail="No chunks created")

        # ------------------------------------------
        # BUILD FAISS INDEX
        # ------------------------------------------
        fm = FaissIndexManager()
        folder = fm.build_index(video_id, chunks, metadatas)

        return {
            "status": "success",
            "video_id": video_id,
            "transcript_path": transcript_path,
            "faiss_folder": folder,
            "chunks": len(chunks)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
