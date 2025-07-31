# app/api.py

from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from app.parser.ner_model import extract_info
from app.retriever.embedder import model as embedder
from app.retriever.vector_store import load_faiss_index, search_clauses
from app.retriever.evaluator import evaluate
from app.reasoner.output_generator import format_output
from pydantic import BaseModel
import os

router = APIRouter()

# Load FAISS index and metadata once (you can load on startup if preferred)
INDEX_PATH = "app/data/embeddings/faiss_index.index"
META_PATH = "app/data/embeddings/metadata.pkl"

try:
    index, metadata = load_faiss_index(INDEX_PATH, META_PATH)
except Exception as e:
    index, metadata = None, []
    print(f"Error loading index: {e}")

DOCS_DIR = "app/data/documents"

class QueryRequest(BaseModel):
    query: str
    domain: str = "insurance"
    use_llm: bool = True
@router.post("/analyze_query")
async def analyze_query(request: QueryRequest):
    if index is None or not metadata:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vector index or metadata not loaded. Please rebuild the index."
        )
    try:
        query_text = request.query
        domain = request.domain

        if not query_text:
            raise HTTPException(status_code=400, detail="Query is required")

        # Step 1: Parse input
        structured = extract_info(query_text, domain=domain)

        # Step 2: Embed and search
        query_embedding = embedder.encode([query_text])[0]
        relevant_clauses = search_clauses(query_embedding, index, metadata, context_window=1, query_text=query_text)

        # Step 3: Evaluate
        evaluation = evaluate(structured, relevant_clauses, domain=domain)

        # Step 4: Output
        return format_output(evaluation, structured)
    except Exception as e:
        print("Internal Server Error:", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}"
        )
@router.post("/upload_document")
async def upload_document(file: UploadFile = File(...)):
    # Save uploaded file
    os.makedirs(DOCS_DIR, exist_ok=True)
    file_path = os.path.join(DOCS_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    # Optionally, trigger ingestion or log
    print(f"Uploaded and saved file: {file.filename}")
    return {"message": "File uploaded and saved successfully."}

@router.get("/list_documents")
async def list_documents():
    try:
        files = os.listdir(DOCS_DIR)
        files = [f for f in files if os.path.isfile(os.path.join(DOCS_DIR, f))]
        return {"documents": files}
    except Exception as e:
        return {"error": str(e)}

@router.post("/rebuild_index")
async def rebuild_index():
    """Rebuild the vector index from documents"""
    try:
        import subprocess
        import sys
        
        # Run the build_vector_index.py script
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "build_vector_index.py")
        result = subprocess.run([sys.executable, script_path], 
                               capture_output=True, 
                               text=True)
        
        if result.returncode == 0:
            # Reload the index
            global index, metadata
            try:
                index, metadata = load_faiss_index(INDEX_PATH, META_PATH)
                return {"message": "Index rebuilt and loaded successfully"}
            except Exception as e:
                return {"error": f"Index rebuilt but failed to load: {str(e)}"}
        else:
            return {"error": f"Failed to rebuild index: {result.stderr}"}
    except Exception as e:
        import traceback
        print("Index Rebuild Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Index Rebuild Error: {str(e)}")
