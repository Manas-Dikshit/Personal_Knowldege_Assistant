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
    # Whitespace-insensitive full-content equality: nothing lost,
    # duplicated (beyond packing), or reordered.
    assert "".join(rebuilt.split()) == "".join(_normalize_markdown(source).split()), \
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
    assert len(chunks) == 2  # one chunk per section
    assert chunks[0]["section"] == "Summary"
    assert chunks[1]["section"] == "Education"


def test_chunk_resume_lossless_short_lines_kept():
    # Single-line items and short sections must survive chunking.
    resume = "\n".join([
        "Manas Ranjan Dikshit",
        "manas@example.com | +91-0000000000",
        "",
        "Education",
        "B.Tech CSE, SUIIT 2024-2028, CGPA 9/10",
        "",
        "Achievements",
        "Hackathon winner",
        "",
        "Certifications",
        "AWS Cloud Practitioner",
    ])
    chunks = chunk_resume(resume)
    rebuilt = "\n\n".join(c["text"] for c in chunks)
    for needle in (
        "manas@example.com", "CGPA 9/10", "Hackathon winner",
        "AWS Cloud Practitioner", "Achievements", "Certifications"
    ):
        assert needle in rebuilt, f"resume content lost: {needle}"
    sections = {c["section"] for c in chunks}
    assert {"Education", "Achievements", "Certifications"} <= sections


# --------------------------------------------------------------------
# github_fetch (mocked HTTP session — no network access)
# --------------------------------------------------------------------

import base64 as _b64
import json as _json

from src import github_fetch as gf


class FakeResponse:
    def __init__(self, status_code=200, payload=None, headers=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.headers = headers or {}

    def json(self):
        return self._payload


def _api_readme_payload(content, name="README.md", size=None, path="README.md",
                        raw_bytes=None):
    raw = raw_bytes if raw_bytes is not None else content.encode("utf-8")
    return {
        "name": name,
        "path": path,
        "sha": "abc123",
        "size": len(raw) if size is None else size,
        "html_url": f"https://github.com/u/repo/blob/main/{path}",
        "download_url": f"https://raw.example/{path}",
        "content": _b64.b64encode(
            raw if isinstance(raw, bytes) else raw.encode("latin-1")
        ).decode("ascii"),
        "encoding": "base64",
    }


def _tmp_fetch_env(monkeypatch_tmpdir):
    gf.DATA_DIR = monkeypatch_tmpdir
    gf.META_PATH = monkeypatch_tmpdir / "readme_meta.json"
    gf.REPOS_PATH = monkeypatch_tmpdir / "repos.json"


def test_fetch_readme_rst_and_case_variants(tmp_path=None):
    import tempfile
    from pathlib import Path as P
    tmp = P(tempfile.mkdtemp())
    _tmp_fetch_env(tmp)

    # GitHub's /readme endpoint resolves any variant; we just handle it.
    original_get = gf.session.get
    try:
        gf.session.get = lambda url, timeout: FakeResponse(
            200, _api_readme_payload("Doc\n====\nRST body text here.",
                                     name="README.rst", path="README.rst"))
        fetched = gf.fetch_readme("repo")
        assert fetched["readme_type"] == "rst"
        assert fetched["content"].endswith("RST body text here.")
    finally:
        gf.session.get = original_get


def test_fetch_readme_missing_404(tmp_path=None):
    import tempfile
    from pathlib import Path as P
    _tmp_fetch_env(P(tempfile.mkdtemp()))
    original_get = gf.session.get
    try:
        gf.session.get = lambda url, timeout: FakeResponse(404, {"message": "Not Found"})
        assert gf.fetch_readme("empty-repo") is None
    finally:
        gf.session.get = original_get


def test_fetch_readme_truncated_then_retry(tmp_path=None):
    import tempfile
    from pathlib import Path as P
    _tmp_fetch_env(P(tempfile.mkdtemp()))
    body = "# Title\n\n" + "content line\n" * 200
    full = _api_readme_payload(body)

    calls = []
    truncated = dict(full)
    truncated["content"] = _b64.b64encode(
        body.encode("utf-8")[:200]).decode("ascii")

    def fake_get(url, timeout):
        calls.append(url)
        if len(calls) == 1:
            return FakeResponse(200, truncated)          # JSON, truncated
        if "raw.example" in url:
            resp = FakeResponse(200)                     # exact bytes
            resp.content = body.encode("utf-8")
            return resp
        return FakeResponse(200, full)

    original_get = gf.session.get
    try:
        gf.session.get = fake_get
        gf.gf_sleep = getattr(gf, "time", None)
        fetched = gf.fetch_readme("repo")
        assert fetched is not None, "raw fallback did not recover"
        assert any("raw.example" in c for c in calls), \
            "did not fall back to raw download URL"
        assert fetched["content"].endswith("content line\n")
    finally:
        gf.session.get = original_get


def test_fetch_readme_utf16_fallback():
    """Non-UTF8 (UTF-16) READMEs must be recovered via raw download."""
    import tempfile
    from pathlib import Path as P
    _tmp_fetch_env(P(tempfile.mkdtemp()))

    utf16_text = "# Railway Deploy Guide\n\nContent with ünïcödé.\n"
    utf16_bytes = b"\xff\xfe" + utf16_text.encode("utf-16-le")

    # GitHub's JSON endpoint reports a size that won't match the mangled
    # base64 text, forcing the raw-bytes fallback.
    payload = _api_readme_payload(utf16_text, raw_bytes=utf16_bytes)
    payload["size"] = len(utf16_text)

    def fake_get(url, timeout):
        if "raw.example" in url:
            resp = FakeResponse(200)
            resp.content = utf16_bytes
            return resp
        return FakeResponse(200, payload)

    original_get = gf.session.get
    try:
        gf.session.get = fake_get
        fetched = gf.fetch_readme("railway-like")
        assert fetched is not None
        assert fetched["content"] == utf16_text, \
            "UTF-16 content not decoded exactly"
    finally:
        gf.session.get = original_get


def test_store_readme_unicode_and_stale_replacement():
    import hashlib
    import tempfile
    from pathlib import Path as P
    tmp = P(tempfile.mkdtemp())
    _tmp_fetch_env(tmp)

    doc = "# Ünïcødé ✓ 日本語 README\n\n| 表 | 列 |\n|----|----|\n| a | b |\n"
    fetched = {
        "content": doc,
        "path": "README.md",
        "name": "README.md",
        "html_url": "https://github.com/u/repo/blob/main/README.md",
        "github_sha": "deadbeef",
        "size_bytes": len(doc.encode("utf-8")),
        "readme_type": "md",
    }

    assert gf.store_readme("uni-repo", fetched) == "created"

    stored = (gf.DATA_DIR / "uni-repo.md").read_text(encoding="utf-8")
    assert stored == doc, "stored README differs byte-for-byte"

    meta = gf.load_meta()["uni-repo"]
    assert meta["sha256"] == hashlib.sha256(doc.encode()).hexdigest()
    assert meta["source_url"].startswith("https://github.com/")
    assert meta["fetched_at"]

    # Unchanged content -> no rewrite.
    assert gf.store_readme("uni-repo", fetched) == "unchanged"

    # Stale local file (different content) -> replaced.
    stale = dict(fetched)
    stale["content"] = doc.replace("日本語", "updated")
    assert gf.store_readme("uni-repo", stale) == "updated"
    assert "updated" in (gf.DATA_DIR / "uni-repo.md").read_text(encoding="utf-8")


def test_ingest_no_silent_loss_end_to_end(tmp_path=None):
    """Stored raw README -> ingestion -> chunks covers all content."""
    import tempfile
    from pathlib import Path as P
    tmp = P(tempfile.mkdtemp())

    readme = (
        "# Repo\n\nIntro with [link](https://x.y).\n\n## Code\n\n"
        "```py\n# hash inside fence\nprint('hi')\n```\n\n"
        "| A | B |\n|---|---|\n| 1 | 2 |\n\nTiny.\n"
    )
    (tmp / "Repo.md").write_text(readme, encoding="utf-8")
    (tmp / "readme_meta.json").write_text(_json.dumps({
        "Repo": {
            "source_url": "https://github.com/u/Repo/blob/main/README.md",
            "fetched_at": "2026-01-01T00:00:00+00:00",
            "sha256": "x",
            "readme_type": "md",
            "path": "README.md",
        }
    }), encoding="utf-8")

    docs = __import__("src.ingest", fromlist=["load_markdown_files"]) \
        .load_markdown_files(str(tmp))
    assert len(docs) == 1
    d = docs[0]
    assert "".join(d["text"].split()) == "".join(readme.split()), \
        "ingestion altered stored README"
    assert d["source_url"].endswith("README.md") and d["readme_type"] == "md"

    chunks = _assert_lossless(readme)
    assert chunks[0]["section"] == "Repo"


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
        test_chunk_resume_lossless_short_lines_kept,
        test_fetch_readme_rst_and_case_variants,
        test_fetch_readme_missing_404,
        test_fetch_readme_truncated_then_retry,
        test_fetch_readme_utf16_fallback,
        test_store_readme_unicode_and_stale_replacement,
        test_ingest_no_silent_loss_end_to_end,
        test_vectorstore_roundtrip,
        test_vectorstore_corrupt_metadata,
    ]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print("\nAll tests passed.")
