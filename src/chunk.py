import re
from typing import Dict, List


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


def _normalize_markdown(text: str) -> str:
    """
    Lossless normalization for markdown: newline style + trailing spaces
    + collapsed blank-line runs. No content is ever removed.
    """

    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# --------------------------------------------------------------------
# Markdown block tokenizer
# --------------------------------------------------------------------

HEADING_RE = re.compile(r"^#{1,6}\s")


def _split_blocks(
    text: str
) -> List[Dict[str, str]]:
    """
    Split markdown into atomic blocks without losing any content.

    Each block is {"section": <current heading title>, "text": <block>}.
    - Heading lines start a new section and stay attached to their content.
    - Fenced code blocks (``` ... ```) are kept whole; '#' inside a fence
      is never treated as a heading.
    - Tables/lists/paragraphs become contiguous-line blocks.
    """

    blocks: List[Dict[str, str]] = []
    section = ""
    buf: List[str] = []
    in_fence = False

    def flush() -> None:
        if buf:
            block_text = "\n".join(buf).strip()
            if block_text:
                blocks.append(
                    {"section": section, "text": block_text}
                )
            buf.clear()

    for line in text.split("\n"):
        stripped = line.strip()

        if stripped.startswith("```"):
            buf.append(line)
            if not in_fence:
                in_fence = True
            else:
                in_fence = False
                flush()
            continue

        if in_fence:
            buf.append(line)
            continue

        if HEADING_RE.match(stripped):
            flush()
            section = stripped.lstrip("#").strip()
            buf.append(line)
            continue

        if not stripped:
            flush()
            continue

        buf.append(line)

    flush()

    return blocks


def _hard_split(
    block: str,
    max_chars: int
) -> List[str]:
    """
    Split an oversized block into contiguous pieces <= max_chars,
    breaking at line boundaries when possible. Nothing is discarded.
    """

    pieces: List[str] = []
    current = ""

    for line in block.split("\n"):

        # Single line longer than max_chars: slice it.
        while len(line) > max_chars:
            if current:
                pieces.append(current)
                current = ""
            pieces.append(line[:max_chars])
            line = line[max_chars:]

        candidate = f"{current}\n{line}" if current else line

        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                pieces.append(current)
            current = line

    if current:
        pieces.append(current)

    return pieces


def chunk_markdown(
    text: str,
    max_chars: int = 800
) -> List[Dict[str, str]]:
    """
    Chunk markdown losslessly.

    Returns [{"text": ..., "section": ...}, ...] such that the chunks
    collectively contain the complete original content (every non-blank
    source line appears exactly once, in order). Small sections are packed
    together instead of being dropped; oversized blocks are split at line
    boundaries.
    """

    normalized = _normalize_markdown(text)

    if not normalized:
        return []

    blocks = _split_blocks(normalized)

    chunks: List[Dict[str, str]] = []
    current_lines: List[str] = []
    current_len = 0
    current_section = ""

    def emit() -> None:
        if current_lines:
            chunks.append(
                {
                    "text": "\n\n".join(current_lines),
                    "section": current_section
                }
            )
            current_lines.clear()
            current_len = 0  # noqa: cannot rebind closure var; handled below

    for block in blocks:

        if len(block["text"]) <= max_chars:
            pieces = [block["text"]]
        else:
            pieces = _hard_split(block["text"], max_chars)

        for piece in pieces:

            if current_lines and current_len + 2 + len(piece) > max_chars:
                chunks.append(
                    {
                        "text": "\n\n".join(current_lines),
                        "section": current_section
                    }
                )
                current_lines = []
                current_len = 0

            if not current_lines:
                current_section = block["section"]

            current_lines.append(piece)
            current_len += (
                len(piece) + (2 if current_len else 0)
            )

    if current_lines:
        chunks.append(
            {
                "text": "\n\n".join(current_lines),
                "section": current_section
            }
        )

    return chunks


def chunk_readme(
    text: str,
    max_chars: int = 800
) -> List[Dict[str, str]]:
    """
    Backwards-compatible alias. Returns [{"text", "section"}, ...].
    """

    return chunk_markdown(text, max_chars)


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
# Contribution / commit logs
# --------------------------------------------------------------------

def chunk_contribution(text: str) -> List[str]:
    """
    Group related contribution lines together.
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
