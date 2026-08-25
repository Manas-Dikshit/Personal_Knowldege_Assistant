from typing import List, Optional

import numpy as np

from src.config import EMBEDDING_MODEL_NAME


class EmbeddingModel:
    """
    Wrapper around SentenceTransformer for document and query embeddings.

    Device-aware (CPU/CUDA), batched, L2-normalized, BGE prefixes.
    """

    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL_NAME,
        batch_size: int = 32
    ):
        # Imported lazily so importing this module doesn't pull in torch
        # unless an embedding is actually needed.
        import torch
        from sentence_transformers import SentenceTransformer

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.batch_size = batch_size

        self.model = SentenceTransformer(
            model_name,
            device=self.device
        )

        self.embedding_dim = (
            self.model.get_sentence_embedding_dimension()
        )

    def embed_documents(
        self,
        texts: List[str],
        normalize: bool = True
    ) -> np.ndarray:
        """
        Embed passages. Returns shape (n_texts, dim), aligned 1:1 with input.
        Raises ValueError on empty/blank entries instead of silently dropping
        them (which would misalign embeddings with their metadata).
        """

        for i, text in enumerate(texts):
            if not text or not text.strip():
                raise ValueError(
                    f"Cannot embed empty text at index {i}."
                )

        passages = [
            f"passage: {text.strip()}"
            for text in texts
        ]

        return self.model.encode(
            passages,
            batch_size=self.batch_size,
            normalize_embeddings=normalize,
            convert_to_numpy=True,
            show_progress_bar=False
        ).astype(np.float32)

    def embed_query(
        self,
        query: str,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Embed a user query. Returns shape (dim,).
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        embedding = self.model.encode(
            f"query: {query.strip()}",
            normalize_embeddings=normalize,
            convert_to_numpy=True
        )

        return embedding.astype(np.float32)

    def similarity(
        self,
        query_embedding: np.ndarray,
        document_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Cosine similarities (embeddings are already L2-normalized).
        """

        return np.dot(
            document_embeddings,
            query_embedding
        )


# Lazy singleton: the heavy model only loads on first use.
_model: Optional[EmbeddingModel] = None


def get_embedding_model() -> EmbeddingModel:
    global _model
    if _model is None:
        _model = EmbeddingModel()
    return _model


def get_embeddings(texts: List[str]) -> np.ndarray:
    """
    Embed a list of documents/chunks.
    """

    return get_embedding_model().embed_documents(texts)


def embed_query(query: str) -> np.ndarray:
    """
    Embed a search query.
    """

    return get_embedding_model().embed_query(query)


# -------------------------------------------------------------------
# Example
# -------------------------------------------------------------------
if __name__ == "__main__":

    docs = [
        "Built a full-stack AI assistant using FastAPI and React.",
        "Developed retrieval-augmented generation pipelines.",
        "Worked with vector databases and semantic search."
    ]

    query = "experience with RAG systems"

    doc_embeddings = get_embeddings(docs)

    query_embedding = embed_query(query)

    scores = get_embedding_model().similarity(
        query_embedding,
        doc_embeddings
    )

    ranked_indices = scores.argsort()[::-1]

    print("\nTop Results:\n")

    for idx in ranked_indices:
        print(
            f"Score: {scores[idx]:.4f} | {docs[idx]}"
        )
