from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np

from src.config import (
    DEFAULT_K,
    SOURCE_PRIORITY,
    SOURCE_BOOST_STRENGTH,
    RERANK_ENABLED,
    RERANK_TOP_N,
    DEDUP_ENABLED,
    DEDUP_THRESHOLD,
)
from src.embed import embed_query
from src.vectorstore import VectorStore


@dataclass
class RetrievedChunk:
    text: str
    score: float
    metadata: Dict


class Retriever:

    def __init__(
        self,
        dim: Optional[int] = None,
        default_k: int = DEFAULT_K
    ):
        self.store = VectorStore(dim=dim)
        self.default_k = default_k

    # ------------------------------------------------------------------
    # Source-aware boost
    # ------------------------------------------------------------------

    def _source_boost(self, metadata: Dict) -> float:
        """Bounded multiplicative score boost for a chunk's source."""
        priority = SOURCE_PRIORITY.get(metadata.get("source", "contributions"), 1.0)
        return 1.0 + (priority - 1.0) * SOURCE_BOOST_STRENGTH

    # ------------------------------------------------------------------
    # Content-based near-duplicate detection
    # ------------------------------------------------------------------

    @staticmethod
    def _container(metadata: Dict) -> tuple:
        """Grouping identity: same source + primary locator.

        Near-duplicates are only considered within the same container so
        cross-source results are never collapsed (e.g. resume 'Python'
        skills vs LinkedIn 'Python' skills stay separate and useful).
        """
        source = metadata.get("source")
        if source == "github":
            return (source, metadata.get("repo"), metadata.get("section"))
        if source == "linkedin":
            return (source, metadata.get("file"), metadata.get("category"))
        if source == "resume":
            return (source, metadata.get("section"))
        return (source,)

    @staticmethod
    def _overlap(text_a: str, text_b: str) -> float:
        """Fraction of the smaller chunk's tokens present in the larger."""
        toks_a = set(text_a.lower().split())
        toks_b = set(text_b.lower().split())
        if not toks_a and not toks_b:
            return 1.0
        if not toks_a or not toks_b:
            return 0.0
        smaller = min(len(toks_a), len(toks_b))
        inter = len(toks_a & toks_b)
        return inter / smaller

    def _apply_dedup(self, results: List[RetrievedChunk]) -> List[RetrievedChunk]:
        """Drop near-duplicate chunks, keeping the highest-scoring one."""
        if not DEDUP_ENABLED:
            return results

        kept: List[RetrievedChunk] = []

        for chunk in results:
            dup = False
            for other in kept:
                if self._container(chunk.metadata) != self._container(other.metadata):
                    continue
                if self._overlap(chunk.text, other.text) >= DEDUP_THRESHOLD:
                    dup = True
                    break
            if not dup:
                kept.append(chunk)

        return kept

    def _rerank(self, results: List[RetrievedChunk]) -> List[RetrievedChunk]:
        """Apply the source boost to top candidates and reorder by it."""
        if not RERANK_ENABLED or not results:
            return results

        for chunk in results:
            chunk.score = chunk.score * self._source_boost(chunk.metadata)

        results.sort(key=lambda c: c.score, reverse=True)
        return results

    # ------------------------------------------------------------------
    # Public retrieval
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        k: Optional[int] = None
    ) -> List[RetrievedChunk]:

        if not query or not query.strip():
            return []

        if k is None:
            k = self.default_k

        # Fetch a superset so dedup + rerank can still yield k results.
        fetch_k = max(k, RERANK_TOP_N)

        query_embedding = np.asarray(
            [embed_query(query)],
            dtype=np.float32
        )

        raw = self.store.search(query_embedding, k=fetch_k)

        chunks = [
            RetrievedChunk(
                text=result["text"],
                score=result["score"],
                metadata=result["metadata"]
            )
            for result in raw
        ]

        chunks = self._apply_dedup(chunks)
        chunks = self._rerank(chunks)

        return chunks[:k]

    def get_context(
        self,
        query: str,
        k: Optional[int] = None
    ) -> str:

        chunks = self.retrieve(query, k)

        return "\n\n".join(chunk.text for chunk in chunks)
