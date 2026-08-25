"""
Minimal self-check for the RAG pipeline's pure logic.
Run:  python tests/test_pipeline.py   (or: pytest tests)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.chunk import (
    chunk_readme,
    chunk_resume,
    clean_text,
    _normalize_markdown
)

from src.vectorstore import VectorStore


def _content_lines(text):
    """Non-blank lines of normalized text, the unit of content coverage."""
    return [
        line for line in _normalize_markdown(text).split("\n")
        if line.strip()
    ]


def _assert_lossless(source, max_chars=800):
    chunks = chunk_readme(source, max_chars=max_chars)
    rebuilt = "\n\n".join(c["text"] for c in chunks)
    assert _content_lines(rebuilt) == _content_lines(source), \
        "chunking lost or reordered README content"
    return chunks


def test_clean_text():
    assert clean_text("a  b\r\n\r\n\r\n c") == "a b\n\n c"
    assert clean_text("") == ""
    assert clean_text("   ") == ""


def test_chunk_readme_keeps_headers():
    md = "# Title\n\nSome intro text here that is long enough.\n\n## Setup\n\nInstall steps described in detail for setup."
    chunks = _assert_lossless(md)
    joined = "\n".join(c["text"] for c in chunks)
    assert "Title" in joined, "header text was dropped"
    assert "Setup" in joined, "subheader text was dropped"


def test_chunk_readme_tiny_file_not_dropped():
    # Regression: a one-line README was previously discarded entirely
    # by the old '<50 chars' section filter.
    chunks = _assert_lossless("# E-cell")
    assert len(chunks) == 1 and "E-cell" in chunks[0]["text"]
    assert chunks[0]["section"] == "E-cell"


def test_chunk_readme_lossless_full_featured():
    md = "\n".join([
        "# Project",
        "",
        "Intro paragraph with [a link](https://example.com) and **bold**.",
        "",
        "## Features",
        "",
        "- list item one",
        "- list item two",
        "  - nested item",
        "",
        "### Code",
        "",
        "```python",
        "# not a heading, even at line start",
        "def f():",
        "    return '```'",
        "```",
        "",
        "## Table",
        "",
        "| Col A | Col B |",
        "|-------|-------|",
        "| 1     | 2     |",
        "",
        "License",
        "",
        "MIT",
    ])
    chunks = _assert_lossless(md)
    sections = {c["section"] for c in chunks}
    assert "Code" in sections and "Table" in sections


def test_chunk_readme_code_fence_hash_not_heading():
    # '#' inside a fence must not start a new section or break the block.
    md = "# Guide\n\n```bash\n# this is a shell comment\npip install x\n```"
    chunks = _assert_lossless(md)
    assert len(chunks) == 1
    fence = [c for c in chunks if "shell comment" in c["text"]][0]
    assert fence["section"] == "Guide"
    assert fence["text"].count("```") == 2, "code fence was split open"


def test_chunk_readme_small_sections_packed_not_dropped():
    md = "# A\n\nshort\n\n# B\n\nalso short\n\n# C\n\ntiny"
    chunks = _assert_lossless(md)
    joined = "\n".join(c["text"] for c in chunks)
    assert all(h in joined for h in ("# A", "# B", "# C"))


def test_chunk_readme_oversize_hard_split_no_loss():
    para = "word " * 400  # single paragraph > max_chars
    md = f"# Big\n\n{para.strip()}"
    chunks = _assert_lossless(md, max_chars=800)
    assert all(len(c["text"]) <= 900 for c in chunks)
    assert len(chunks) > 1


def test_chunk_readme_single_long_line():
    line = "x" * 3000
    md = f"# T\n\n{line}"
    chunks = _assert_lossless(md, max_chars=800)
    rebuilt = "".join(c["text"] for c in chunks)
    assert "x" * 3000 in rebuilt.replace("\n\n", "").replace("\n", "")


def test_chunk_resume_sections():
    resume = (
        "Summary\n" + "x" * 100
        + "\n\nEducation\n" + "y" * 100
    )
    chunks = chunk_resume(resume)
    assert len(chunks) == 1  # both sections pack under the buffer limit
    assert "Summary" in chunks[0] and "Education" in chunks[0]


def test_vectorstore_roundtrip(tmp_path=None):
    import faiss
    import numpy as np

    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())

    store = VectorStore(
        dim=4,
        index_path=tmp_path / "i.faiss",
        metadata_path=tmp_path / "m.json",
    )

    vecs = np.eye(4, dtype=np.float32)
    store.add(vecs, ["a", "b", "c", "d"], [{"id": i} for i in range(4)])
    store.save()

    # Dim mismatch must be rejected, not silently corrupt.
    try:
        store.add(np.zeros((1, 3), dtype=np.float32), ["bad"])
        raise AssertionError("dim mismatch not caught")
    except ValueError:
        pass

    reloaded = VectorStore(
        index_path=tmp_path / "i.faiss",
        metadata_path=tmp_path / "m.json",
    )
    assert len(reloaded) == 4
    assert reloaded.dim == 4  # dim comes from stored index

    hits = reloaded.search(np.eye(4, dtype=np.float32)[0], k=2)
    assert len(hits) == 2 and hits[0]["text"] == "a"


def test_vectorstore_corrupt_metadata():
    import faiss
    import numpy as np
    import tempfile

    tmp = Path(tempfile.mkdtemp())
    index = faiss.IndexFlatIP(4)
    index.add(np.eye(4, dtype=np.float32))
    faiss.write_index(index, str(tmp / "i.faiss"))
    (tmp / "m.json").write_text("[]", encoding="utf-8")

    try:
        VectorStore(index_path=tmp / "i.faiss", metadata_path=tmp / "m.json")
        raise AssertionError("corrupt metadata not detected")
    except RuntimeError:
        pass


if __name__ == "__main__":
    tests = [
        test_clean_text,
        test_chunk_readme_keeps_headers,
        test_chunk_readme_tiny_file_not_dropped,
        test_chunk_readme_lossless_full_featured,
        test_chunk_readme_code_fence_hash_not_heading,
        test_chunk_readme_small_sections_packed_not_dropped,
        test_chunk_readme_oversize_hard_split_no_loss,
        test_chunk_readme_single_long_line,
        test_chunk_resume_sections,
        test_vectorstore_roundtrip,
        test_vectorstore_corrupt_metadata,
    ]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print("\nAll tests passed.")
