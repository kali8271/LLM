# AI Document Analysis System

This project is an AI-powered document analysis platform built with FastAPI (backend) and Gradio (frontend). It allows users to upload documents, analyze queries using LLM-based reasoning, and manage a searchable vector index of document content.

---

## Features

- **Query Analysis:** Enter queries and receive structured decisions, justifications, and relevant document clauses.
- **Chat Interface:** Chat with the system about your documents.
- **Document Management:** Upload, list, and re-index documents (PDF, DOCX, TXT).
- **Vector Search:** Uses FAISS for fast semantic search over document embeddings.
- **LLM Reasoning:** Optionally use a language model for advanced reasoning.

---

## Project Structure

```
e:\LLM\
│
├── app\
│   ├── main.py            # FastAPI entry point
│   ├── api.py             # FastAPI API routes
│   ├── gradio_ui.py       # Gradio UI frontend
│   ├── parser\
│   ├── retriever\
│   ├── reasoner\
│   └── data\
│       └── documents\     # Uploaded documents
│       └── embeddings\    # FAISS index and metadata
│
├── scripts\
│   └── build_vector_index.py
│
└── README.md
```

---

## Setup Instructions

1. **Clone the repository**  
   ```bash
   git clone <your-repo-url>
   cd LLM
   ```

2. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the FastAPI backend**  
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Start the Gradio frontend**  
   ```bash
   python app/gradio_ui.py
   ```

5. **Access the UI**  
   Open the Gradio link printed in your terminal (e.g., http://127.0.0.1:7860).

---

## Usage

- **Query Analysis:** Enter a question and select a domain to analyze.
- **Chat:** Interact conversationally about your documents.
- **Upload Documents:** Upload PDF, DOCX, or TXT files for indexing.
- **Rebuild Index:** Click "Rebuild Vector Index" after uploading new documents.

---

## Enhancements & Next Steps

1. **Improve error handling and user feedback in both backend and frontend.**
2. **Add authentication for secure document access.**
3. **Support more document formats and preview in UI.**
4. **Add automated tests for endpoints and UI functions.**
5. **Dockerize the project for easy deployment.**
6. **Add environment variable support for configuration.**
7. **Optimize vector search and index loading for large datasets.**
8. **Enhance UI/UX with progress indicators and better layout.**

---

## License

MIT License

---

## Contact

For questions or contributions, please open an issue or pull request.

---

## More About the Project

### How It Works

1. **Document Ingestion:**  
   Users upload documents (PDF, DOCX, TXT) via the Gradio UI. These documents are stored and can be indexed for semantic search.

2. **Vector Indexing:**  
   The system uses embedding models to convert document text into vectors. These vectors are stored in a FAISS index for efficient similarity search.

3. **Query Analysis:**  
   When a user submits a query, the backend:
   - Parses and extracts structured information using NER and domain-specific logic.
   - Embeds the query and searches for the most relevant clauses in the indexed documents.
   - Optionally uses an LLM for advanced reasoning and justification.
   - Returns a structured response with decision, amount, justification, relevant clauses, and extracted entities.

4. **Chat Interface:**  
   Users can interact conversationally with the system, asking questions about the uploaded documents and receiving context-aware answers.

5. **Document Management:**  
   Users can view the list of indexed documents, upload new ones, and trigger re-indexing as needed.

---

### Technologies Used

- **FastAPI:** High-performance backend for API endpoints.
- **Gradio:** User-friendly web UI for interaction.
- **FAISS:** Efficient vector similarity search.
- **Transformers/Sentence Transformers:** For generating embeddings.
- **NER Models:** For extracting structured information from text.
- **Python:** Core programming language for all components.

---

### Typical Use Cases

- **Legal Document Analysis:** Extracting and reasoning over clauses in contracts or policies.
- **Insurance Claims:** Analyzing insurance documents and claims for decision support.
- **Enterprise Document Search:** Semantic search and Q&A over large collections of business documents.

---

### Customization

- **Add New Domains:** Extend the parser and evaluator modules to support new document types or industries.
- **Swap Embedding Models:** Use different transformer models for embeddings based on your accuracy and speed requirements.
- **Integrate Other LLMs:** Plug in different language models for reasoning (e.g., OpenAI, Azure, local models).

---

### Contribution

We welcome contributions! Please fork the repo, create a branch, and submit a pull request. For major changes, open an issue first to discuss your