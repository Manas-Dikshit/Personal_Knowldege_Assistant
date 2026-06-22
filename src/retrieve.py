import numpy as np
from src.embed import embed_single
from src.vectorstore import VectorStore


class Retriever:
    def __init__(self, dim):
        self.store = VectorStore(dim=dim)

    def search(self, query, k=5):
        # 1. convert query → embedding
        q_vec = embed_single(query)

        # 2. reshape for FAISS
        q_vec = np.array([q_vec]).astype("float32")

        # 3. search in vector DB
        results = self.store.search(q_vec, k=k)

        return results