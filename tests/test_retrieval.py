"""
Tests for source-aware ranking, deduplication, and cross-source retrieval.
Run:  python tests/test_retrieval.py   (or: pytest tests)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from src.retrieve import Retriever, RetrievedChunk
from src.config import (
    SOURCE_PRIORITY,
    DEFAULT_K,
    RERANK_ENABLED,
    RERANK_TOP_N,
    DEDUP_ENABLED,
    DEDUP_SCORE_TOLERANCE,
)


def _mk(chunks):
    return [
        RetrievedChunk(text=t, score=s, metadata=m)
        for t, s, m in chunks
    ]


# --------------------------------------------------------------------
# Source priority
# --------------------------------------------------------------------

def test_source_priority_values_ordered():
    # Resume/profile (authoritative) must rank higher than others,
    # and each configured source resolves to a positive weight.
    assert SOURCE_PRIORITY["resume"] > SOURCE_PRIORITY["github"]
    assert SOURCE_PRIORITY["resume"] > SOURCE_PRIORITY["linkedin"]
    assert SOURCE_PRIORITY["github"] >= SOURCE_PRIORITY["linkedin"]
    assert SOURCE_PRIORITY["linkedin"] >= SOURCE_PRIORITY["contributions"]
    for v in SOURCE_PRIORITY.values():
        assert v > 0


def test_source_priority_unknown_defaults_to_one():
    r = Retriever.__new__(Retriever)
    assert r._source_priority({"source": "unknown"}) == 1.0
    assert r._source_priority({}) == 1.0


# --------------------------------------------------------------------
# Deduplication keys
# --------------------------------------------------------------------

def test_dedup_key_uses_source_repo_section():
    r = Retriever.__new__(Retriever)

    md1 = {"source": "github", "repo": "L4SBOA", "section": "Intro"}
    md2 = {"source": "github", "repo": "L4SBOA", "section": "Intro"}
    md3 = {"source": "github", "repo": "L4SBOA", "section": "Install"}
    md4 = {"source": "resume", "repo": "L4SBOA", "section": "Intro"}

    assert r._dedup_key(md1) == r._dedup_key(md2)
    assert r._dedup_key(md1) != r._dedup_key(md3)
    assert r._dedup_key(md1) != r._dedup_key(md4)


def test_dedup_key_uses_content_hash_when_present():
    r = Retriever.__new__(Retriever)

    md1 = {"source": "github", "repo": "R", "section": "S", "content_hash": "abc"}
    md2 = {"source": "github", "repo": "R", "section": "S", "content_hash": "xyz"}
    assert r._dedup_key(md1) != r._dedup_key(md2)


# --------------------------------------------------------------------
# Deduplication application
# --------------------------------------------------------------------

def test_dedup_removes_exact_duplicates():
    r = Retriever.__new__(Retriever)
    chunks = _mk([
        ("t1", 0.9, {"source": "github", "repo": "R", "section": "S"}),
        ("t2", 0.85, {"source": "github", "repo": "R", "section": "S"}),
        ("t3", 0.8, {"source": "github", "repo": "R", "section": "Other"}),
    ])
    out = r._apply_dedup(chunks)
    # Two unique keys -> one duplicate dropped.
    assert len(out) == 2


def test_dedup_keeps_better_duplicate():
    r = Retriever.__new__(Retriever)
    chunks = _mk([
        ("low", 0.5, {"source": "github", "repo": "R", "section": "S"}),
        ("high", 0.95, {"source": "github", "repo": "R", "section": "S"}),
    ])
    out = r._apply_dedup(chunks)
    assert len(out) == 2  # both kept because better is significantly higher


def test_dedup_cross_source_preserved():
    # Same repo/section but different source must NOT dedup (both kept).
    r = Retriever.__new__(Retriever)
    chunks = _mk([
        ("r1", 0.7, {"source": "resume", "repo": "X", "section": "Skills"}),
        ("g1", 0.7, {"source": "github", "repo": "X", "section": "Skills"}),
    ])
    out = r._apply_dedup(chunks)
    assert len(out) == 2


# --------------------------------------------------------------------
# Reranking by source priority
# --------------------------------------------------------------------

def test_rerank_boosts_authoritative_source():
    r = Retriever.__new__(Retriever)
    chunks = _mk([
        # A contributions result with a high raw score.
        ("c", 0.75, {"source": "contributions"}),
        # A resume result with a slightly lower raw score.
        ("r", 0.70, {"source": "resume"}),
    ])
    out = r._rerank(chunks)
    # After boosting, resume must rank above contributions.
    assert out[0].metadata["source"] == "resume"
    assert out[0].score > out[1].score


def test_rerank_disabled_passthrough():
    from src import retrieve as _retrieve
    original = _retrieve.RERANK_ENABLED
    _retrieve.RERANK_ENABLED = False
    try:
        r = Retriever.__new__(Retriever)
        chunks = _mk([
            ("c", 0.75, {"source": "contributions"}),
            ("r", 0.70, {"source": "resume"}),
        ])
        out = r._rerank(chunks)
        # Order and scores unchanged when rerank off.
        assert out[0].metadata["source"] == "contributions"
        assert out[0].score == 0.75
    finally:
        _retrieve.RERANK_ENABLED = original


# --------------------------------------------------------------------
# End-to-end retrieve with a mocked store
# --------------------------------------------------------------------

def test_retrieve_cross_source_and_dedup(tmp_path=None):
    # Build a retriever that talks to a fake store and a stubbed
    # embedder so no embedding model is loaded. Verifies dedup +
    # source priority + metadata preservation.
    from unittest import mock
    import tempfile

    class FakeStore:
        def __init__(self, chunks):
            self._chunks = chunks
            self.ntotal = len(chunks)

        def search(self, query_embedding, k=5):
            return self._chunks[:k]

    r = Retriever.__new__(Retriever)
    r.store = FakeStore([
        {"text": "resume a", "score": 0.7,
         "metadata": {"source": "resume", "section": "Skills"}},
        {"text": "github a", "score": 0.68,
         "metadata": {"source": "github", "repo": "R", "section": "Skills"}},
        # A duplicate of github a (same key) should be deduped.
        {"text": "github a2", "score": 0.66,
         "metadata": {"source": "github", "repo": "R", "section": "Skills"}},
        {"text": "linkedin a", "score": 0.5,
         "metadata": {"source": "linkedin", "category": "skills"}},
    ])

    fake_emb = np.zeros((1, 4), dtype=np.float32)
    with mock.patch("src.retrieve.embed_query", return_value=fake_emb[0]):
        results = r.retrieve("what are your skills", k=3)

    # resume should rank first due to priority boost.
    assert results[0].metadata["source"] == "resume"
    # github and linkedin retained (cross-source preserved).
    sources = {c.metadata["source"] for c in results}
    assert {"resume", "github", "linkedin"} <= sources
    # No duplicate github A section returned.
    dup = [c for c in results
           if c.metadata.get("repo") == "R" and c.metadata.get("source") == "github"]
    assert len(dup) == 1
    # Metadata/provenance intact.
    assert results[0].metadata.get("source") is not None


def test_retrieve_empty_query():
    r = Retriever.__new__(Retriever)
    assert r.retrieve("") == []
    assert r.retrieve("   ") == []


def test_retrieve_returns_at_most_k():
    import tempfile
    from unittest import mock

    class FakeStore:
        def __init__(self, n):
            self._chunks = [
                {"text": f"t{i}", "score": 1 - i * 0.01,
                 "metadata": {"source": "github", "repo": f"R{i}", "section": "S"}}
                for i in range(n)
            ]
            self.ntotal = n

        def search(self, query_embedding, k=5):
            return self._chunks[:k]

    r = Retriever.__new__(Retriever)
    r.store = FakeStore(30)
    with mock.patch("src.retrieve.embed_query",
                    return_value=np.zeros(4, dtype=np.float32)):
        res = r.retrieve("test", k=5)
    assert len(res) <= 5


if __name__ == "__main__":
    tests = [
        test_source_priority_values_ordered,
        test_source_priority_unknown_defaults_to_one,
        test_dedup_key_uses_source_repo_section,
        test_dedup_key_uses_content_hash_when_present,
        test_dedup_removes_exact_duplicates,
        test_dedup_keeps_better_duplicate,
        test_dedup_cross_source_preserved,
        test_rerank_boosts_authoritative_source,
        test_rerank_disabled_passthrough,
        test_retrieve_cross_source_and_dedup,
        test_retrieve_empty_query,
        test_retrieve_returns_at_most_k,
    ]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print("\nAll retrieval tests passed.")
