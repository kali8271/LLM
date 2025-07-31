# app/retriever/embedder.py

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed_text(texts: list[str]):
    return model.encode(texts, show_progress_bar=False)
