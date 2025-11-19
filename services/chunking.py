# services/chunking.py
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_text_from_segments(segments: List[Dict], chunk_size: int = 800, chunk_overlap: int = 50) -> List[str]:
    """
    Build chunk list from whisper segments (each segment has 'text', 'start', 'end').
    If `segments` is empty, return [] and caller may fall back to transcript text splitting.
    Returns list of chunk strings in order.
    """
    if not segments:
        return []

    # Join segments into a single text but keep boundaries approximate
    full_text = " ".join(seg.get("text", "") for seg in segments).strip()

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = [c.strip() for c in splitter.split_text(full_text) if c and c.strip()]

    return chunks
