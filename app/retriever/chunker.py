# app/retriever/chunker.py

import re

def split_text_to_chunks(text, max_len=300, overlap=50, strategy="paragraph", context_window=0):
    """
    Split text into chunks using the specified strategy.
    - strategy: 'paragraph', 'section', or 'sentence'
    - context_window: number of neighboring chunks to include as context
    Returns a list of (section_header, chunk_text) tuples.
    """
    import re
    chunks = []
    section_header = None

    if strategy == "paragraph":
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        for para in paragraphs:
            # Detect section headers (e.g., lines in ALL CAPS or starting with 'SECTION')
            if re.match(r'^[A-Z\s\d:]+$', para) or para.lower().startswith('section'):
                section_header = para
            else:
                chunks.append((section_header, para))
    elif strategy == "section":
        # Split on lines that look like section headers
        raw_chunks = re.split(r'(?m)^([A-Z][A-Z\s]+:|\d+\.|[IVX]+\.|Section \d+)', text)
        raw_chunks = [c.strip() for c in raw_chunks if c.strip()]
        for chunk in raw_chunks:
            if re.match(r'^[A-Z\s\d:]+$', chunk) or chunk.lower().startswith('section'):
                section_header = chunk
            else:
                chunks.append((section_header, chunk))
    else:  # sentence
        sentences = text.split('. ')
        chunk = ""
        for sentence in sentences:
            if len(chunk) + len(sentence) <= max_len:
                chunk += sentence + ". "
            else:
                chunks.append((section_header, chunk.strip()))
                chunk = sentence + ". "
        if chunk:
            chunks.append((section_header, chunk.strip()))

    # Add overlap and context window if needed (not implemented for section headers here)
    return chunks

if __name__ == "__main__":
    # Unit tests for split_text_to_chunks
    sample_text = """Section 1\nThis is the first paragraph.\n\nSection 2\nThis is the second paragraph. It has two sentences.\n\nSection 3\nA short one."""

    # Test paragraph strategy
    chunks = split_text_to_chunks(sample_text, strategy="paragraph")
    print("Paragraph chunks:", chunks)
    assert len(chunks) == 6, f"Expected 6 paragraphs, got {len(chunks)}"

    # Test section strategy
    chunks = split_text_to_chunks(sample_text, strategy="section")
    print("Section chunks:", chunks)
    assert any("Section 1" in c for c in chunks), "Section 1 should be in a chunk"

    # Test sentence strategy
    chunks = split_text_to_chunks(sample_text, strategy="sentence", max_len=50)
    print("Sentence chunks:", chunks)
    assert any("first paragraph." in c for c in chunks), "Sentence chunking failed"

    # Test context window
    chunks = split_text_to_chunks(sample_text, strategy="paragraph", context_window=1)
    print("Paragraph chunks with context:", chunks)
    assert all("Section" in c for c in chunks), "Context window should include section headers"

    print("All tests passed.")
