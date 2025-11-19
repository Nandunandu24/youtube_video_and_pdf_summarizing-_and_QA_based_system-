# services/run_day5.py
import json, os
from services.chunking import chunk_text_from_segments
from services.embeddings_index import FaissIndexManager

TRANSCRIPT_PATH = "transcripts/sample_transcript.json"  # replace with actual transcript path

def load_transcript(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Expecting whisper-style result: data["segments"] = list of {start,end,text}
    return data

def main():
    if not os.path.exists(TRANSCRIPT_PATH):
        print("Transcript file not found:", TRANSCRIPT_PATH)
        return

    data = load_transcript(TRANSCRIPT_PATH)
    segments = data.get("segments", [])
    if not segments:
        print("No segments in transcript.")
        return

    print("Chunking text...")
    chunks, metadatas = chunk_text_from_segments(segments, chunk_size=1000, chunk_overlap=200)
    print(f"Created {len(chunks)} chunks.")

    print("Building FAISS index (this may take a while)...")
    manager = FaissIndexManager(model_name="all-MiniLM-L6-v2", index_path="faiss.index", meta_path="index_meta.pkl")
    manager.build_index(chunks, metadatas, batch_size=64)
    print("Index built and saved.")

    # test query
    question = "What does the video say about model deployment?"
    print("\nQuerying index with:", question)
    results = manager.query(question, k=4)
    for r in results:
        print("----")
        print("start:", r.get("start"), "end:", r.get("end"))
        print("preview:", r.get("text_preview")[:300])

if __name__ == "__main__":
    main()
