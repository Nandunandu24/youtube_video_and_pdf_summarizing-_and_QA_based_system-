# routes/files.py
from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid
from services.file_reader import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_txt,
    extract_text_from_csv
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from services.embeddings_index import FaissIndexManager

router = APIRouter(prefix="/files", tags=["Files"])

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        ext = file.filename.split(".")[-1].lower()
        file_id = f"file_{uuid.uuid4().hex[:8]}"
        save_path = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")

        with open(save_path, "wb") as f:
            f.write(await file.read())

        # Extract text
        if ext == "pdf":
            full_text = extract_text_from_pdf(save_path)
        elif ext == "docx":
            full_text = extract_text_from_docx(save_path)
        elif ext == "txt":
            full_text = extract_text_from_txt(save_path)
        elif ext == "csv":
            full_text = extract_text_from_csv(save_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        if not full_text.strip():
            raise HTTPException(status_code=400, detail="File contains no readable text.")

        # Chunking
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        chunks = splitter.split_text(full_text)

        # Metadata
        metadata = [
            {"start": i, "end": i + 1, "chunk_text": ch}
            for i, ch in enumerate(chunks)
        ]

        # FAISS
        fm = FaissIndexManager()
        folder = fm.build_index(file_id, chunks, metadata)

        return {
            "status": "success",
            "file_id": file_id,
            "chunks": len(chunks),
            "faiss_folder": folder
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {e}")
