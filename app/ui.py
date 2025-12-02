import streamlit as st
import httpx
import re
import time
from datetime import datetime
from PyPDF2 import PdfReader
import docx

API_URL = "http://localhost:8000/api/analyze_query"
UPLOAD_URL = "http://localhost:8000/api/upload_document"
LIST_URL = "http://localhost:8000/api/list_documents"
REBUILD_URL = "http://localhost:8000/api/rebuild_index"
DELETE_URL = "http://localhost:8000/api/delete_document"


# ---------- Backend Functions ----------
def analyze(query, domain, use_llm=True):
    try:
        with httpx.Client(timeout=120) as client:
            response = client.post(
                API_URL,
                json={"query": query, "domain": domain, "use_llm": use_llm},
            )
        if response.status_code != 200:
            return {"error": f"❌ Error {response.status_code}"}
        return response.json()
    except Exception as e:
        return {"error": f"⚠️ Error: {str(e)}"}


def upload_document(file):
    if file is None:
        return "No file uploaded."
    try:
        with httpx.Client(timeout=120) as client:
            files = {"file": (file.name, file.getvalue(), file.type or "application/octet-stream")}
            response = client.post(UPLOAD_URL, files=files)
        if response.status_code == 200:
            return "✅ Document uploaded and ingested successfully!"
        else:
            return f"❌ Upload failed ({response.status_code})."
    except Exception:
        return "⚠️ Error: Could not upload document."


@st.cache_data(ttl=60)
def list_documents():
    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(LIST_URL)
        if response.status_code == 200:
            data = response.json()
            return data.get("documents", [])
        else:
            return []
    except Exception:
        return []


def delete_document(filename):
    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(DELETE_URL, json={"filename": filename})
        if response.status_code == 200:
            return "✅ Document deleted successfully!"
        else:
            return f"❌ Error {response.status_code}"
    except Exception:
        return "⚠️ Error: Could not delete document."


def rebuild_index():
    try:
        with httpx.Client(timeout=120) as client:
            response = client.post(REBUILD_URL)
        if response.status_code == 200:
            return "✅ Index rebuilt successfully!"
        else:
            return f"❌ Error: {response.text}"
    except Exception:
        return "⚠️ Error: Could not rebuild index."


# ---------- Helpers ----------
def stream_response(text):
    placeholder = st.empty()
    final_output = ""
    for word in text.split():
        final_output += word + " "
        placeholder.markdown(final_output)
        time.sleep(0.03)
    return final_output


def extract_preview(file):
    preview_text = ""
    try:
        if file.name.endswith(".pdf"):
            reader = PdfReader(file)
            for i, page in enumerate(reader.pages[:2]):
                preview_text += page.extract_text() + "\n"
        elif file.name.endswith(".docx"):
            doc = docx.Document(file)
            for para in doc.paragraphs[:10]:
                preview_text += para.text + "\n"
        elif file.name.endswith(".txt"):
            preview_text = file.read().decode("utf-8").split("\n", 20)
            preview_text = "\n".join(preview_text)
    except Exception as e:
        preview_text = f"⚠️ Could not extract preview: {str(e)}"
    return preview_text[:1500]


# ---------- Entity Highlighter ----------
def highlight_entities(text: str) -> str:
    # Dates
    text = re.sub(r"\b(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})\b",
                  r'<span style="background-color:#FFD580; padding:2px 4px; border-radius:4px;">\1</span>',
                  text)

    # Organizations
    text = re.sub(r"\b([A-Z][a-zA-Z]+ (?:Ltd|Inc|Corp|Company|LLP))\b",
                  r'<span style="background-color:#B0E0E6; padding:2px 4px; border-radius:4px;">\1</span>',
                  text)

    # Parties
    text = re.sub(r"\b(Claimant|Respondent|Insurer|Policyholder|Defendant|Plaintiff)\b",
                  r'<span style="background-color:#98FB98; padding:2px 4px; border-radius:4px;">\1</span>',
                  text)

    # Jurisdictions
    text = re.sub(r"\b([A-Z][a-z]+ (Court|Tribunal|Arbitration))\b",
                  r'<span style="background-color:#FFB6C1; padding:2px 4px; border-radius:4px;">\1</span>',
                  text)

    return text


# ---------- Streamlit App ----------
def main():
    st.set_page_config(page_title="AI Document Analysis System", layout="wide")
    st.title("📑 AI Document Analysis System")

    tab1, tab2, tab3 = st.tabs(["🔍 Query Analysis", "💬 Chat Interface", "📂 Document Management"])

    # -------- Tab 1: Query Analysis --------
    with tab1:
        domain = st.selectbox("Select Domain", ["insurance", "legal"], index=0)
        if domain == "insurance":
            st.info("💡 Example: 'What is the claim settlement process?'")
        elif domain == "legal":
            st.info("💡 Example: 'What clauses mention arbitration?'")

        query = st.text_area("Enter your query", height=100)
        use_llm = st.checkbox("Use LLM for reasoning", value=True)

        if st.button("Analyze"):
            with st.spinner("🔎 Analyzing..."):
                result = analyze(query, domain, use_llm)

            if "error" in result:
                st.error(result["error"])
            else:
                answer = result.get("answer", "")
                sources = result.get("sources", [])

                with st.expander("📌 Analysis Result", expanded=True):
                    st.markdown(highlight_entities(answer), unsafe_allow_html=True)

                if sources:
                    with st.expander("📂 Retrieved Clauses / Sources"):
                        for src in sources:
                            st.markdown(highlight_entities(src), unsafe_allow_html=True)

    # -------- Tab 2: Chat Interface --------
    with tab2:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        domain_chat = st.selectbox("Select Domain (Chat)", ["insurance", "legal"], index=0, key="chat_domain")
        use_llm_chat = st.checkbox("Use LLM", value=True, key="chat_llm")

        docs = list_documents()
        selected_docs = st.multiselect("Select documents to include in chat context", docs, default=docs[:1])

        # Display chat history
        for user_msg, bot_msg, timestamp in st.session_state.chat_history:
            with st.chat_message("user", avatar="📘"):
                st.markdown(f"{user_msg}\n\n ⏱️ *{timestamp}*")
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(highlight_entities(bot_msg), unsafe_allow_html=True)

        # New chat input
        if prompt := st.chat_input("Ask about your selected documents..."):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with st.chat_message("user", avatar="📘"):
                st.markdown(f"{prompt}\n\n ⏱️ *{timestamp}*")

            with st.chat_message("assistant", avatar="🤖"):
                placeholder = st.empty()
                final_answer = ""

                try:
                    with httpx.Client(timeout=120) as client:
                        response = client.post(
                            API_URL,
                            json={
                                "query": prompt,
                                "domain": domain_chat,
                                "use_llm": use_llm_chat,
                                "documents": selected_docs
                            },
                        )
                    if response.status_code == 200:
                        result = response.json()
                        final_answer = result.get("answer", "")
                        sources = result.get("sources", [])

                        placeholder.markdown(highlight_entities(final_answer), unsafe_allow_html=True)

                        if sources:
                            with st.expander("📂 Sources"):
                                for src in sources:
                                    st.markdown(highlight_entities(src), unsafe_allow_html=True)
                    else:
                        final_answer = f"❌ Error {response.status_code}"
                        placeholder.error(final_answer)
                except Exception as e:
                    final_answer = f"⚠️ Error: {str(e)}"
                    placeholder.error(final_answer)

            st.session_state.chat_history.append((prompt, final_answer, timestamp))

        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()

    # -------- Tab 3: Document Management --------
    with tab3:
        uploaded_file = st.file_uploader("Upload Document (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        if uploaded_file:
            st.subheader("📄 Document Preview")
            preview = extract_preview(uploaded_file)
            st.text(preview)

            if st.button("Upload and Ingest"):
                with st.spinner("📤 Uploading..."):
                    status = upload_document(uploaded_file)
                st.success(status) if "✅" in status else st.error(status)

        st.subheader("📑 Indexed Documents")
        docs = list_documents()
        if docs:
            selected_doc = st.selectbox("Select a document", docs)
            if st.button("Delete Document"):
                with st.spinner("🗑 Deleting..."):
                    status = delete_document(selected_doc)
                st.success(status) if "✅" in status else st.error(status)
        else:
            st.info("No documents found.")

        if st.button("Rebuild Vector Index"):
            with st.spinner("⚙️ Rebuilding index..."):
                status = rebuild_index()
            if "✅" in status:
                st.success(status)
            else:
                st.error(status)


if __name__ == "__main__":
    main()
