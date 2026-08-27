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
    SOURCE_BOOST_STRENGTH,
    DEFAULT_K,
    RERANK_ENABLED,
    RERANK_TOP_N,
    DEDUP_ENABLED,
    DEDUP_THRESHOLD,
)


def _mk(chunks):
    return [
        RetrievedChunk(text=t, score=s, metadata=m)
        for t, s, m in chunks
    ]


# --------------------------------------------------------------------
# Source priority / boost
# --------------------------------------------------------------------

def test_source_priority_values_ordered():
    # Resume/profile (authoritative) must rank higher than others.
    assert SOURCE_PRIORITY["resume"] > SOURCE_PRIORITY["github"]
    assert SOURCE_PRIORITY["resume"] > SOURCE_PRIORITY["linkedin"]
    assert SOURCE_PRIORITY["github"] >= SOURCE_PRIORITY["linkedin"]
    assert SOURCE_PRIORITY["linkedin"] >= SOURCE_PRIORITY["contributions"]
    for v in SOURCE_PRIORITY.values():
        assert v > 0


def test_source_boost_bounds_scores():
    # Boost must be small and not blow cosine scores out of range.
    r = Retriever.__new__(Retriever)
    assert r._source_boost({"source": "resume"}) > r._source_boost({"source": "github"})
    assert r._source_boost({"source": "github"}) >= r._source_boost({"source": "linkedin"})
    # Even the strongest (resume) keeps scores near/under 1 for raw ~0.9.
    assert r._source_boost({"source": "resume"}) < 1.2


def test_source_boost_unknown_defaults_to_one():
    r = Retriever.__new__(Retriever)
    assert r._source_boost({"source": "unknown"}) == 1.0
    assert r._source_boost({}) == 1.0


# --------------------------------------------------------------------
# Container grouping
# --------------------------------------------------------------------

def test_container_grouping_cross_source_distinct():
    r = Retriever.__new__(Retriever)
    resume = {"source": "resume", "section": "Skills"}
    linkedin = {"source": "linkedin", "file": "Skills.csv", "category": "skills"}
    github = {"source": "github", "repo": "R", "section": "Skills"}
    assert r._container(resume) != r._container(linkedin)
    assert r._container(linkedin) != r._container(github)


def test_container_same_source_similar_collapses():
    r = Retriever.__new__(Retriever)
    a = {"source": "github", "repo": "R", "section": "S"}
    b = {"source": "github", "repo": "R", "section": "S"}
    c = {"source": "github", "repo": "R", "section": "Other"}
    assert r._container(a) == r._container(b)
    assert r._container(a) != r._container(c)


# --------------------------------------------------------------------
# Content overlap
# --------------------------------------------------------------------

def test_overlap_identical():
    r = Retriever.__new__(Retriever)
    assert r._overlap("python docker fastapi", "python docker fastapi") == 1.0


def test_overlap_disjoint():
    r = Retriever.__new__(Retriever)
    assert r._overlap("python docker", "react node") == 0.0


def test_overlap_partial():
    r = Retriever.__new__(Retriever)
    # 1 of 2 tokens overlap -> 0.5 (smaller set is size 2)
    assert r._overlap("python docker", "python react") == 0.5


# --------------------------------------------------------------------
# Deduplication application
# --------------------------------------------------------------------

def test_dedup_removes_near_duplicates_same_container():
    r = Retriever.__new__(Retriever)
    chunks = _mk([
        ("python docker fastapi sqlite", 0.9,
         {"source": "github", "repo": "R", "section": "S"}),
        ("python docker fastapi sqlite redis", 0.85,
         {"source": "github", "repo": "R", "section": "S"}),
        ("react node typescript", 0.8,
         {"source": "github", "repo": "R", "section": "S"}),
    ])
    out = r._apply_dedup(chunks)
    # First two overlap heavily -> one dropped; third kept.
    assert len(out) == 2


def test_dedup_preserves_distinct_linkedin_chunks():
    # Distinct skill subsets must NOT collapse through dedup.
    r = Retriever.__new__(Retriever)
    chunks = _mk([
        ("LinkedIn skills: python docker fastapi", 0.8,
         {"source": "linkedin", "file": "Skills.csv", "category": "skills"}),
        ("LinkedIn skills: react node typescript", 0.79,
         {"source": "linkedin", "file": "Skills.csv", "category": "skills"}),
        ("LinkedIn skills: docker kubernetes", 0.78,
         {"source": "linkedin", "file": "Skills.csv", "category": "skills"}),
    ])
    out = r._apply_dedup(chunks)
    assert len(out) == 3


def test_dedup_preserves_cross_source():
    # Same topic from different sources must both be kept.
    r = Retriever.__new__(Retriever)
    chunks = _mk([
        ("python docker fastapi", 0.7,
         {"source": "resume", "section": "Skills"}),
        ("python docker fastapi", 0.7,
         {"source": "github", "repo": "X", "section": "Skills"}),
    ])
    out = r._apply_dedup(chunks)
    assert len(out) == 2


# --------------------------------------------------------------------
# Reranking by source priority
# --------------------------------------------------------------------

def test_rerank_boosts_authoritative_source():
    r = Retriever.__new__(Retriever)
    chunks = _mk([
        ("contribution log content", 0.75, {"source": "contributions"}),
        ("resume summary content", 0.70, {"source": "resume"}),
    ])
    out = r._rerank(chunks)
    # Resume gets a boost and must now rank above the higher raw contributor.
    assert out[0].metadata["source"] == "resume"
    assert out[0].score > out[1].score
    # Scores stay in a sane range.
    assert 0 <= out[0].score <= 1.2


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
        assert out[0].metadata["source"] == "contributions"
        assert out[0].score == 0.75
    finally:
        _retrieve.RERANK_ENABLED = original


# --------------------------------------------------------------------
# End-to-end retrieve with a mocked store
# --------------------------------------------------------------------

def test_retrieve_cross_source_and_dedup(tmp_path=None):
    # Fake store + stubbed embedder: no model loaded.
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
        {"text": "resume summary python docker", "score": 0.7,
         "metadata": {"source": "resume", "section": "Summary"}},
        {"text": "github repo python docker ", "score": 0.68,
         "metadata": {"source": "github", "repo": "R", "section": "Intro"}},
        # Near-duplicate of github a (same container) -> dropped.
        {"text": "github repo python docker redis", "score": 0.66,
         "metadata": {"source": "github", "repo": "R", "section": "Intro"}},
        {"text": "linkedin skills react node", "score": 0.5,
         "metadata": {"source": "linkedin", "file": "Skills.csv", "category": "skills"}},
    ])

    fake_emb = np.zeros(4, dtype=np.float32)
    with mock.patch("src.retrieve.embed_query", return_value=fake_emb):
        results = r.retrieve("what are your skills", k=3)

    # resume boosted to the top.
    assert results[0].metadata["source"] == "resume"
    # Cross-source preserved: github + linkedin still present.
    sources = {c.metadata["source"] for c in results}
    assert {"resume", "github", "linkedin"} <= sources
    # Near-duplicate github dropped.
    github = [c for c in results if c.metadata.get("source") == "github"]
    assert len(github) == 1
    # Provenance intact.
    assert all(c.metadata.get("source") for c in results)


def test_retrieve_empty_query():
    r = Retriever.__new__(Retriever)
    assert r.retrieve("") == []
    assert r.retrieve("   ") == []


def test_retrieve_returns_at_most_k():
    from unittest import mock

    class FakeStore:
        def __init__(self, n):
            self._chunks = [
                {"text": f"topic content block {i}", "score": 1 - i * 0.05,
                 "metadata": {"source": "github", "repo": f"R{i % 5}", "section": "S"}}
                for i in range(n)
            ]
            self.ntotal = n

        def search(self, query_embedding, k=5):
            return self._chunks[:k]

    r = Retriever.__new__(Retriever)
    r.store = FakeStore(40)
    with mock.patch("src.retrieve.embed_query",
                    return_value=np.zeros(4, dtype=np.float32)):
        res = r.retrieve("test", k=5)
    assert len(res) <= 5


if __name__ == "__main__":
    tests = [
        test_source_priority_values_ordered,
        test_source_boost_bounds_scores,
        test_source_boost_unknown_defaults_to_one,
        test_container_grouping_cross_source_distinct,
        test_container_same_source_similar_collapses,
        test_overlap_identical,
        test_overlap_disjoint,
        test_overlap_partial,
        test_dedup_removes_near_duplicates_same_container,
        test_dedup_preserves_distinct_linkedin_chunks,
        test_dedup_preserves_cross_source,
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
