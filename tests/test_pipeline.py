"""
Minimal self-check for the RAG pipeline's pure logic.
Run:  python tests/test_pipeline.py   (or: pytest tests)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.chunk import chunk_readme, chunk_resume, clean_text

from src.vectorstore import VectorStore


def test_clean_text():
    assert clean_text("a  b\r\n\r\n\r\n c") == "a b\n\n c"
    assert clean_text("") == ""
    assert clean_text("   ") == ""


def test_chunk_readme_keeps_headers():
    md = "# Title\n\nSome intro text here that is long enough.\n\n## Setup\n\nInstall steps described in detail for setup."
    chunks = chunk_readme(md)
    assert len(chunks) >= 2
    assert any("Title" in c for c in chunks), "header text was dropped"
    assert any("Setup" in c for c in chunks), "subheader text was dropped"


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
        test_chunk_resume_sections,
        test_vectorstore_roundtrip,
        test_vectorstore_corrupt_metadata,
    ]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print("\nAll tests passed.")
