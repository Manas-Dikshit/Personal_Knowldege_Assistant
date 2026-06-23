from typing import List
import numpy as np
import torch
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """
    Wrapper around SentenceTransformer for document and query embeddings.

    Features
    --------
    - Device-aware (CPU / CUDA)
    - Batched encoding
    - L2 normalization
    - Proper BGE prefixes
    - Empty input handling
    - Numpy output
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5",
        batch_size: int = 32
    ):
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
        Embed passages/documents.

        Parameters
        ----------
        texts : List[str]
            List of document chunks.

        normalize : bool
            Apply L2 normalization.

        Returns
        -------
        np.ndarray
            Shape: (n_documents, embedding_dim)
        """

        if not texts:
            return np.empty(
                (0, self.embedding_dim),
                dtype=np.float32
            )

        passages = [
            f"passage: {text.strip()}"
            for text in texts
            if text and text.strip()
        ]

        if not passages:
            return np.empty(
                (0, self.embedding_dim),
                dtype=np.float32
            )

        embeddings = self.model.encode(
            passages,
            batch_size=self.batch_size,
            normalize_embeddings=normalize,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        return embeddings

    def embed_query(
        self,
        query: str,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Embed a user query.

        Parameters
        ----------
        query : str
            Search query.

        normalize : bool
            Apply L2 normalization.

        Returns
        -------
        np.ndarray
            Shape: (embedding_dim,)
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        embedding = self.model.encode(
            f"query: {query.strip()}",
            normalize_embeddings=normalize,
            convert_to_numpy=True
        )

        return embedding

    def similarity(
        self,
        query_embedding: np.ndarray,
        document_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute cosine similarities.

        Parameters
        ----------
        query_embedding : np.ndarray
            Query vector.

        document_embeddings : np.ndarray
            Matrix of document vectors.

        Returns
        -------
        np.ndarray
            Similarity scores.
        """

        return np.dot(
            document_embeddings,
            query_embedding
        )


# -------------------------------------------------------------------
# Singleton instance
# -------------------------------------------------------------------

embedding_model = EmbeddingModel()


# -------------------------------------------------------------------
# Convenience functions
# -------------------------------------------------------------------

def get_embeddings(texts: List[str]) -> np.ndarray:
    """
    Embed a list of documents/chunks.
    """

    return embedding_model.embed_documents(texts)


def embed_single(text: str) -> np.ndarray:
    """
    Embed a single document.
    """

    embeddings = embedding_model.embed_documents([text])

    return embeddings[0]


def embed_query(query: str) -> np.ndarray:
    """
    Embed a search query.
    """

    return embedding_model.embed_query(query)


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

    scores = embedding_model.similarity(
        query_embedding,
        doc_embeddings
    )

    ranked_indices = scores.argsort()[::-1]

    print("\nTop Results:\n")

    for idx in ranked_indices:
        print(
            f"Score: {scores[idx]:.4f} | {docs[idx]}"
        )