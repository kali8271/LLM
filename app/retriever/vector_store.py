# app/retriever/vector_store.py

import faiss
import numpy as np
import pickle
from sentence_transformers import CrossEncoder

EMBED_DIM = 384  # For all-MiniLM-L6-v2

def load_faiss_index(index_path, metadata_path):
    index = faiss.read_index(index_path)
    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

def search_clauses(query_embedding, index, metadata, top_k=3, context_window=1, query_text=None):
    D, I = index.search(np.array([query_embedding]), top_k)
    candidates = []
    for i in I[0]:
        context = []
        for offset in range(-context_window, context_window + 1):
            idx = i + offset
            if 0 <= idx < len(metadata):
                context.append(metadata[idx])
        candidate = "\n---\n".join(context)
        candidates.append(candidate)
    # Rerank with cross-encoder if query_text is provided
    if query_text is not None and candidates:
        pairs = [(query_text, c) for c in candidates]
        scores = cross_encoder.predict(pairs)
        reranked = [c for _, c in sorted(zip(scores, candidates), reverse=True)]
        return reranked
    return candidates
