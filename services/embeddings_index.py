# services/embeddings_index.py
import os
import pickle
import faiss
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

class FaissIndexManager:
    def __init__(self, index_dir: str = "faiss_index"):
        self.index_dir = index_dir
        os.makedirs(self.index_dir, exist_ok=True)

        # ✅ Local embedding model
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.current_video_id = None

    def _get_video_index_path(self, video_id: str) -> str:
        return os.path.join(self.index_dir, video_id)

    def _get_latest_video_id(self) -> Optional[str]:
        subfolders = [os.path.join(self.index_dir, d) for d in os.listdir(self.index_dir) if os.path.isdir(os.path.join(self.index_dir, d))]
        if not subfolders:
            return None
        latest_folder = max(subfolders, key=os.path.getmtime)
        return os.path.basename(latest_folder)

    def build_index(self, video_id: str, chunks: List[str], metadatas: List[Dict]):
        video_index_path = self._get_video_index_path(video_id)
        os.makedirs(video_index_path, exist_ok=True)

        print(f"🧠 Building FAISS index for {video_id} ...")

        vectors = np.array(self.embedder.encode(chunks, show_progress_bar=True)).astype("float32")

        d = vectors.shape[1]
        index = faiss.IndexFlatL2(d)
        index.add(vectors)

        index_path = os.path.join(video_index_path, "index.faiss")
        meta_path = os.path.join(video_index_path, "meta.pkl")

        faiss.write_index(index, index_path)
        with open(meta_path, "wb") as f:
            pickle.dump(metadatas, f)

        print(f"✅ Index saved to {index_path}")
        return video_index_path

    def load_index(self, video_id: Optional[str] = None):
        if video_id is None:
            video_id = self._get_latest_video_id()
            if not video_id:
                raise FileNotFoundError("No FAISS index found.")

        video_index_path = self._get_video_index_path(video_id)
        index_file = os.path.join(video_index_path, "index.faiss")

        self.index = faiss.read_index(index_file)
        self.current_video_id = video_id
        print(f"✅ Loaded FAISS index for {video_id}")
        return self.index

    def search(self, video_id: Optional[str], query: str, top_k: int = 5):
        if video_id is None:
            video_id = self._get_latest_video_id()

        if self.index is None or self.current_video_id != video_id:
            self.load_index(video_id)

        meta_path = os.path.join(self._get_video_index_path(video_id), "meta.pkl")
        with open(meta_path, "rb") as f:
            metadatas = pickle.load(f)

        query_vec = np.array(self.embedder.encode([query])).astype("float32")
        distances, indices = self.index.search(query_vec, top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(metadatas):
                m = dict(metadatas[idx])
                m["distance"] = float(dist)
                results.append(m)

        print(f"🔍 Found {len(results)} chunks for query '{query}'")
        return results
