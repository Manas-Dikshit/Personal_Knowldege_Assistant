import re


# -------------------------
# Generic text cleaner
# -------------------------
def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# -------------------------
# Smart chunker
# -------------------------
def chunk_text(text, chunk_size=800, overlap=150):
    """
    Generic semantic-ish chunking using sliding window
    """
    text = clean_text(text)

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(chunk)
        start = end - overlap

    return chunks


# -------------------------
# Resume chunking (structured)
# -------------------------
def chunk_resume(text):
    text = clean_text(text)

    # split by sections if possible
    sections = re.split(r'\n\s*\n', text)

    chunks = [s.strip() for s in sections if len(s.strip()) > 50]

    return chunks


# -------------------------
# README chunking (better quality)
# -------------------------
def chunk_readme(text):
    text = clean_text(text)

    # split by headings or paragraphs
    parts = re.split(r'\n#{1,6}|\n\n', text)

    chunks = [p.strip() for p in parts if len(p.strip()) > 40]

    return chunks


# -------------------------
# Contribution chunking
# -------------------------
def chunk_contribution(text):
    text = clean_text(text)

    lines = text.split("\n")

    chunks = [line.strip() for line in lines if len(line.strip()) > 20]

    return chunks