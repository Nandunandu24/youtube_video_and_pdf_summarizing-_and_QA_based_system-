# services/summarize.py
import os
import json
import pickle
import psutil
from transformers import pipeline
from fastapi import HTTPException

# ======================================================
# ⚙️ Adaptive lightweight summarization model
# ======================================================
available_gb = psutil.virtual_memory().available / (1024 ** 3)

if available_gb < 4:
    SUM_MODEL = "sshleifer/distilbart-cnn-12-6"  # ✅ very small
elif available_gb < 8:
    SUM_MODEL = "facebook/bart-base"
else:
    SUM_MODEL = "facebook/bart-large-cnn"

print(f"🔧 Loading summarization model: {SUM_MODEL} (RAM: {available_gb:.2f} GB)")

try:
    summarizer = pipeline("summarization", model=SUM_MODEL)
    print(f"✅ Summarizer loaded successfully: {SUM_MODEL}")
except Exception as e:
    raise RuntimeError(f"❌ Failed to load summarization model: {str(e)}")


def _chunk_text(text: str, max_chars: int = 2500):
    """Split long text into smaller chunks for summarization."""
    paragraphs = []
    current_chunk = ""

    for sentence in text.split(". "):
        if len(current_chunk) + len(sentence) < max_chars:
            current_chunk += sentence + ". "
        else:
            paragraphs.append(current_chunk.strip())
            current_chunk = sentence + ". "

    if current_chunk:
        paragraphs.append(current_chunk.strip())
    return paragraphs


def generate_summary_json(video_id: str, max_chunks: int = 30):
    """
    Offline summarization using lightweight BART models.
    Automatically adapts to low-RAM environments.
    """
    base = os.path.join("faiss_index", video_id)
    meta_path = os.path.join(base, "meta.pkl")

    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Metadata not found for video {video_id}.")

    with open(meta_path, "rb") as f:
        meta = pickle.load(f)

    # Combine transcript text
    text_segments = []
    for m in meta[:max_chunks]:
        txt = m.get("chunk_text", "")
        start, end = m.get("start", 0), m.get("end", 0)
        text_segments.append(f"[{start:.1f}s–{end:.1f}s] {txt}")

    full_text = " ".join(text_segments).strip()
    if not full_text:
        raise HTTPException(status_code=400, detail="No transcript content found.")

    print(f"🧩 Splitting long transcript for summarization...")
    chunks = _chunk_text(full_text, max_chars=2500)
    print(f"✂️ Created {len(chunks)} safe summarization chunks.")

    summaries = []
    for i, chunk in enumerate(chunks, 1):
        print(f"🧠 Summarizing chunk {i}/{len(chunks)} ...")
        try:
            result = summarizer(chunk, max_length=200, min_length=60, do_sample=False)
            summaries.append(result[0]["summary_text"].strip())
        except Exception as e:
            print(f"⚠️ Skipping chunk {i} due to error: {e}")
            continue

    if not summaries:
        raise HTTPException(status_code=500, detail="All summarization chunks failed.")

    # Combine all partial summaries
    combined_summary = " ".join(summaries)

    outline = [
        {
            "topic": "Main Highlights",
            "bullets": combined_summary.split(". ")[:3],
            "timestamp": "00:00–End",
        }
    ]

    quiz = [
        {
            "question": "What is the video mainly about?",
            "options": ["Introduction", "Main topic", "Unrelated", "Conclusion"],
            "answer": "Main topic",
        }
    ]

    summary_json = {
        "title": f"Summary for {video_id}",
        "outline": outline,
        "summary": combined_summary,
        "quiz": quiz,
    }

    os.makedirs("summaries", exist_ok=True)
    output_path = os.path.join("summaries", f"{video_id}_summary.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary_json, f, indent=2, ensure_ascii=False)

    print(f"✅ [summarize] Saved summary at {output_path}")
    return summary_json
