from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np

from src.config import (
    DEFAULT_K,
    SOURCE_PRIORITY,
    RERANK_ENABLED,
    RERANK_TOP_N,
    DEDUP_ENABLED,
    DEDUP_SCORE_TOLERANCE,
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

    def _source_priority(self, metadata: Dict) -> float:
        """Return the priority weight for a result's source."""
        source = metadata.get("source", "contributions")
        return SOURCE_PRIORITY.get(source, 1.0)

    def _dedup_key(self, metadata: Dict) -> str:
        """Create a deduplication key from metadata."""
        source = metadata.get("source", "")
        repo = metadata.get("repo") or ""
        section = metadata.get("section") or ""
        # Include content hash if available
        content_hash = metadata.get("content_hash", "")
        if content_hash:
            return f"{source}:{repo}:{section}:{content_hash[:12]}"
        return f"{source}:{repo}:{section}"

    def _apply_dedup(self, results: List[RetrievedChunk]) -> List[RetrievedChunk]:
        """Remove near-duplicate results based on dedup keys."""
        if not DEDUP_ENABLED:
            return results

        seen = {}
        filtered = []

        for chunk in results:
            key = self._dedup_key(chunk.metadata)

            if key in seen:
                existing = seen[key]
                # Keep the one with higher adjusted score
                if chunk.score > existing.score + DEDUP_SCORE_TOLERANCE:
                    # New one is significantly better, replace
                    seen[key] = chunk
                    filtered.append(chunk)
                # else: keep existing, skip this duplicate
            else:
                seen[key] = chunk
                filtered.append(chunk)

        return filtered

    def _rerank(self, results: List[RetrievedChunk]) -> List[RetrievedChunk]:
        """Lightweight reranking: apply source priority to scores."""
        if not RERANK_ENABLED or len(results) <= 1:
            return results

        # Take top N candidates for reranking
        candidates = results[:RERANK_TOP_N]

        for chunk in candidates:
            priority = self._source_priority(chunk.metadata)
            # Adjust score: original score * priority
            # Blend with a small base to avoid extreme swings
            chunk.score = chunk.score * 0.7 + (priority * 0.3)

        # Re-sort by adjusted score
        candidates.sort(key=lambda c: c.score, reverse=True)

        # Return candidates + remaining in order
        remaining = results[RERANK_TOP_N:]
        return candidates + remaining

    def retrieve(
        self,
        query: str,
        k: Optional[int] = None
    ) -> List[RetrievedChunk]:

        if not query or not query.strip():
            return []

        if k is None:
            k = self.default_k

        # Embed query and shape for FAISS.
        query_embedding = np.asarray(
            [embed_query(query)],
            dtype=np.float32
        )

        # Fetch a superset of results to allow dedup + reranking to
        # keep k after filtering. Cap the superset to stay cheap.
        fetch_k = max(k, RERANK_TOP_N)

        results = self.store.search(
            query_embedding,
            k=fetch_k
        )

        # Convert to RetrievedChunk objects
        chunks = [
            RetrievedChunk(
                text=result["text"],
                score=result["score"],
                metadata=result["metadata"]
            )
            for result in results
        ]

        # Apply deduplication
        chunks = self._apply_dedup(chunks)

        # Apply source-aware reranking
        chunks = self._rerank(chunks)

        # Re-sort by final adjusted score (rerank may have re-ordered)
        chunks.sort(key=lambda c: c.score, reverse=True)

        # Return top-k after reranking
        return chunks[:k]

    def get_context(
        self,
        query: str,
        k: Optional[int] = None
    ) -> str:

        chunks = self.retrieve(
            query,
            k
        )

        return "\n\n".join(
            chunk.text
            for chunk in chunks
        )
