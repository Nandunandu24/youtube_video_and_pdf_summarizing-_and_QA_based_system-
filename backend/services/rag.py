# services/rag.py
import os
from typing import Dict, Any, List
import psutil
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from services.embeddings_index import FaissIndexManager

MODEL_NAME = os.environ.get("RAG_MODEL", "google/flan-t5-base")
print(f"🔧 Loading RAG model: {MODEL_NAME} (Free RAM: {psutil.virtual_memory().available/1024**3:.2f} GB)")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def _unique_lines_across_chunks(retrieved: List[Dict], max_chars: int = 1800) -> str:
    seen = set()
    parts = []
    total_chars = 0

    for r in sorted(retrieved, key=lambda x: x.get("distance", 0.0)):  # best first
        text = r.get("chunk_text", "") or ""
        # break into lines (sentences)
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        for ln in lines:
            if ln in seen:
                continue
            seen.add(ln)
            snippet = ln
            if total_chars + len(snippet) > max_chars:
                # stop gracefully if adding this line would overflow
                return "\n".join(parts)
            parts.append(snippet)
            total_chars += len(snippet)
    return "\n".join(parts)

def _generate_from_prompt(prompt: str, max_new_tokens: int = 200) -> str:
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    out = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        num_beams=4,
        no_repeat_ngram_size=3,
        early_stopping=True
    )
    return tokenizer.decode(out[0], skip_special_tokens=True).strip()

def rag_answer(video_id: str, question: str, top_k: int = 5) -> Dict[str, Any]:
    try:
        fm = FaissIndexManager()
        fm.load_index(video_id)

        retrieved = fm.search(video_id, question, top_k=top_k)
        if not retrieved:
            return {"answer": "No relevant information found.", "sources": []}

        # Build a deduplicated context across chunks (avoid repeating same lines)
        context = _unique_lines_across_chunks(retrieved, max_chars=1800)
        if not context or len(context.strip()) < 20:
            return {"answer": "No relevant information found.", "sources": []}

        prompt = f"""
You are an assistant answering questions using ONLY the CONTEXT below.
If the answer can't be found in CONTEXT, reply EXACTLY: "No relevant information found."
Do NOT invent facts. Be concise.

CONTEXT:
{context}

QUESTION:
{question}

Answer (short and factual):
""".strip()

        answer = _generate_from_prompt(prompt, max_new_tokens=200)

        return {
            "answer": answer,
            "sources": [
                {"start": r.get("start"), "end": r.get("end"), "text": (r.get("chunk_text") or "")[:200]}
                for r in retrieved
            ]
        }

    except Exception as e:
        raise RuntimeError(f"RAG error: {e}")
