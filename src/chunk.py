import re
from typing import List


# --------------------------------------------------------------------
# Text cleanup
# --------------------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Normalize whitespace while preserving paragraph boundaries.
    """

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # remove trailing spaces
    text = re.sub(r"[ \t]+", " ", text)

    # normalize excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# --------------------------------------------------------------------
# Paragraph splitter
# --------------------------------------------------------------------

def split_paragraphs(text: str) -> List[str]:
    """
    Split text into logical paragraphs.
    """

    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n", text)
        if p.strip()
    ]

    return paragraphs


# --------------------------------------------------------------------
# Sentence splitter
# --------------------------------------------------------------------

def split_sentences(text: str) -> List[str]:
    """
    Lightweight sentence segmentation.
    """

    sentences = re.split(
        r'(?<=[.!?])\s+(?=[A-Z])',
        text
    )

    return [s.strip() for s in sentences if s.strip()]


# --------------------------------------------------------------------
# Generic semantic chunking
# --------------------------------------------------------------------

def chunk_text(
    text: str,
    max_chars: int = 900,
    overlap_chars: int = 150
) -> List[str]:
    """
    Create chunks while preserving paragraph boundaries.

    Uses paragraph packing instead of naive slicing.
    """

    text = clean_text(text)

    paragraphs = split_paragraphs(text)

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:

        if len(paragraph) > max_chars:
            sentences = split_sentences(paragraph)

            for sentence in sentences:

                candidate = (
                    current_chunk + " " + sentence
                ).strip()

                if len(candidate) <= max_chars:
                    current_chunk = candidate

                else:

                    if current_chunk:
                        chunks.append(current_chunk)

                    current_chunk = sentence

            continue

        candidate = (
            current_chunk + "\n\n" + paragraph
        ).strip()

        if len(candidate) <= max_chars:
            current_chunk = candidate

        else:

            if current_chunk:
                chunks.append(current_chunk)

            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    # overlap
    final_chunks = []

    for i, chunk in enumerate(chunks):

        if i == 0:
            final_chunks.append(chunk)
            continue

        prev = chunks[i - 1]

        overlap = prev[-overlap_chars:]

        final_chunks.append(
            overlap + "\n\n" + chunk
        )

    return final_chunks


# --------------------------------------------------------------------
# Resume chunking
# --------------------------------------------------------------------

RESUME_HEADERS = [
    "summary",
    "education",
    "experience",
    "projects",
    "skills",
    "certifications",
    "achievements",
    "publications",
    "volunteering"
]


def chunk_resume(text: str) -> List[str]:
    """
    Chunk resumes by sections.
    """

    text = clean_text(text)

    pattern = (
        r"(?i)(?=^("
        + "|".join(RESUME_HEADERS)
        + r")\b)"
    )

    sections = re.split(
        pattern,
        text,
        flags=re.MULTILINE
    )

    chunks = []

    buffer = ""

    for section in sections:

        section = section.strip()

        if len(section) < 40:
            continue

        buffer += "\n\n" + section

        if len(buffer) >= 300:
            chunks.append(buffer.strip())
            buffer = ""

    if buffer:
        chunks.append(buffer.strip())

    return chunks


# --------------------------------------------------------------------
# README chunking
# --------------------------------------------------------------------

def chunk_readme(text: str) -> List[str]:
    """
    Preserve markdown structure.
    """

    text = clean_text(text)

    sections = re.split(
        r"(?m)^#{1,6}\s+",
        text
    )

    chunks = []

    for section in sections:

        section = section.strip()

        if len(section) < 50:
            continue

        if len(section) <= 1200:
            chunks.append(section)

        else:
            chunks.extend(
                chunk_text(
                    section,
                    max_chars=900
                )
            )

    return chunks


# --------------------------------------------------------------------
# Contribution / commit logs
# --------------------------------------------------------------------

def chunk_contribution(text: str) -> List[str]:
    """
    Group related contribution lines together
    instead of treating every line independently.
    """

    text = clean_text(text)

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    chunks = []
    current = ""

    for line in lines:

        candidate = (
            current + "\n" + line
        ).strip()

        if len(candidate) < 600:
            current = candidate

        else:
            chunks.append(current)
            current = line

    if current:
        chunks.append(current)

    return chunks