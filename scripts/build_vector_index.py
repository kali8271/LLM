# scripts/build_vector_index.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import faiss
import pickle
import pdfplumber
import docx

from app.retriever.chunker import split_text_to_chunks
from app.retriever.embedder import model as embedder

DOCS_DIR = "app/data/documents"
os.makedirs(DOCS_DIR, exist_ok=True)  # <-- Ensure the directory exists
INDEX_PATH = "app/data/embeddings/faiss_index.index"
META_PATH = "app/data/embeddings/metadata.pkl"

# Chunking strategy and context window can be adjusted here
CHUNK_STRATEGY = "paragraph"  # options: 'paragraph', 'section', 'sentence'
CONTEXT_WINDOW = 1  # number of neighboring chunks to include

def load_documents(folder_path):
    docs = []
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                docs.append((filename, f.read()))
        elif filename.endswith(".pdf"):
            with pdfplumber.open(filepath) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                docs.append((filename, text))
        elif filename.endswith(".docx"):
            doc = docx.Document(filepath)
            text = "\n".join([para.text for para in doc.paragraphs])
            docs.append((filename, text))
    return docs

# ...existing code...

def build_index():
    print("Loading documents...")
    documents = load_documents(DOCS_DIR)

    all_chunks = []
    metadata = []

    for filename, text in documents:
        chunks = split_text_to_chunks(text, strategy=CHUNK_STRATEGY, context_window=CONTEXT_WINDOW)
        for section_header, chunk in chunks:
            all_chunks.append(chunk)
            meta = f"{filename} :: "
            if section_header:
                meta += f"[{section_header}] "
            meta += chunk
            metadata.append(meta)

    print(f"Embedding {len(all_chunks)} chunks...")
    if not all_chunks:
        print("No document chunks found. Please add valid documents to app/data/documents.")
        return

    embeddings = embedder.encode(all_chunks, show_progress_bar=True)

    print("Building FAISS index...")
    dim = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    print("Saving FAISS index and metadata...")
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print("Done!")

if __name__ == "__main__":
    build_index()

    # Simple ingestion tests for PDF and DOCX
    test_dir = "app/data/documents"
    docs = load_documents(test_dir)
    print(f"Loaded {len(docs)} documents from {test_dir}")
    for fname, text in docs:
        print(f"{fname}: {len(text)} characters")
        assert isinstance(text, str) and len(text) > 0, f"Document {fname} is empty or not a string"
    print("PDF/DOCX/txt ingestion test passed.")