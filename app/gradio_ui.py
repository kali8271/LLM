# app/gradio_ui.py

import gradio as gr
import requests
import re
import json

API_URL = "http://localhost:8000/api/analyze_query"
UPLOAD_URL = "http://localhost:8000/api/upload_document"
LIST_URL = "http://localhost:8000/api/list_documents"
REBUILD_URL = "http://localhost:8000/api/rebuild_index"

# Function to call FastAPI backend for analysis
def analyze(query, domain, use_llm=True):
    response = requests.post(API_URL, json={"query": query, "domain": domain, "use_llm": use_llm})
    if response.status_code == 200:
        result = response.json()
        output = f"""### Query Analysis Result\n\n**Decision:** {result['decision']}  \n**Amount:** {result['amount']}\n\n**Justification:** {result['justification']}\n\n---\n\n"""
        
        # Add reasoning if available
        if 'reasoning' in result:
            output += f"**LLM Reasoning:**\n{result['reasoning']}\n\n---\n"
        
        output += "**Relevant Clauses:**\n"
        parties = result.get('parties', [])
        for clause in result['clauses']:
            # Extract section header if present in the clause metadata
            match = re.match(r'([^:]+) :: \[(.*?)\] (.*)', clause)
            if match:
                filename, section_header, chunk_text = match.groups()
                output += f"\n**{section_header}**\n"
                highlighted_clause = chunk_text
            else:
                highlighted_clause = clause
            for party in parties:
                if party:
                    highlighted_clause = highlighted_clause.replace(party, f"**{party}**")
            output += f"- {highlighted_clause}\n"
        # Add legal-specific fields if present
        if parties:
            output += f"\n**Parties:** {', '.join(parties)}"
        organizations = result.get('organizations', [])
        if organizations:
            output += f"\n**Organizations:** {', '.join(organizations)}"
        dates = result.get('dates', [])
        if dates:
            output += f"\n**Dates:** {', '.join(dates)}"
        if 'jurisdiction' in result and result['jurisdiction']:
            output += f"\n**Jurisdiction:** {result['jurisdiction']}"
        return output
    else:
        return f"Error: {response.text}"

# Function to upload document to backend
def upload_document(file):
    if file is None:
        return "No file uploaded."
    try:
        if hasattr(file, "read"):
            # Binary file (PDF, DOCX)
            content = file.read()
        elif hasattr(file, "value"):
            # Text file (TXT)
            content = file.value.encode("utf-8")
        else:
            return "Unsupported file type."
        files = {"file": (file.name, content, file.type if hasattr(file, 'type') else "application/octet-stream")}
        response = requests.post(UPLOAD_URL, files=files)
        if response.status_code == 200:
            return "Document uploaded and ingested successfully!"
        else:
            return f"Upload failed: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def list_documents():
    try:
        response = requests.get(LIST_URL)
        if response.status_code == 200:
            data = response.json()
            if "documents" in data:
                return "\n".join(data["documents"])
            else:
                return "No documents found."
        else:
            return f"Error: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def rebuild_index():
    try:
        response = requests.post(REBUILD_URL)
        if response.status_code == 200:
            return "Index rebuilt successfully!"
        else:
            return f"Error: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# Chat function for the chat interface
def chat(message, history, domain, use_llm=True):
    history.append((message, ""))
    response = analyze(message, domain, use_llm)
    history[-1] = (message, response)
    return history

# Gradio UI
def main():
    with gr.Blocks(title="AI Document Analysis System") as demo:
        gr.Markdown("# AI Document Analysis System\nEnter your query, select a domain, upload documents, and get structured decisions with justifications.")
        
        with gr.Tabs():
            with gr.TabItem("Query Analysis"):
                with gr.Row():
                    query = gr.Textbox(label="Enter your query", lines=3)
                    domain = gr.Dropdown(choices=["insurance", "legal"], value="insurance", label="Domain")
                
                with gr.Row():
                    analyze_btn = gr.Button("Analyze")
                    use_llm = gr.Checkbox(label="Use LLM for reasoning", value=True)
                
                output = gr.Markdown(label="Result")
                analyze_btn.click(fn=lambda q, d, l: analyze(q, d, use_llm=l), 
                                 inputs=[query, domain, use_llm], 
                                 outputs=output)
            
            with gr.TabItem("Chat Interface"):
                chatbot = gr.Chatbot(height=400, type="messages")
                chat_input = gr.Textbox(label="Ask about your documents", lines=2)
                with gr.Row():
                    chat_domain = gr.Dropdown(choices=["insurance", "legal"], value="insurance", label="Domain")
                    chat_use_llm = gr.Checkbox(label="Use LLM", value=True)
                
                chat_input.submit(fn=lambda m, h, d, l: chat(m, h, d, l), 
                                inputs=[chat_input, chatbot, chat_domain, chat_use_llm], 
                                outputs=[chatbot])
                clear_btn = gr.Button("Clear Chat")
                clear_btn.click(lambda: None, None, chatbot, queue=False)
            
            with gr.TabItem("Document Management"):
                gr.Markdown("## Upload Document (PDF, DOCX, TXT)")
                file_input = gr.File(label="Upload Document", file_types=[".pdf", ".docx", ".txt"])
                upload_btn = gr.Button("Upload and Ingest")
                upload_output = gr.Textbox(label="Upload Status", lines=2)
                upload_btn.click(fn=upload_document, inputs=file_input, outputs=upload_output)
                
                gr.Markdown("## Indexed Documents")
                doc_list = gr.Textbox(label="Indexed Documents", lines=5, interactive=False)
                refresh_btn = gr.Button("Refresh Document List")
                refresh_btn.click(fn=list_documents, inputs=None, outputs=doc_list)
                
                # Index rebuilding button
                rebuild_btn = gr.Button("Rebuild Vector Index")
                rebuild_status = gr.Textbox(label="Rebuild Status", lines=2)
                rebuild_btn.click(fn=rebuild_index, inputs=None, outputs=rebuild_status)
        
        # Auto-refresh on load
        demo.load(fn=list_documents, inputs=None, outputs=doc_list)

if __name__ == "__main__":
    main()