import numpy as np
from src.embed import embed_single
from src.vectorstore import VectorStore


class RAGQueryEngine:
    def __init__(self, dim):
        self.store = VectorStore(dim=dim)

    def ask(self, question, k=5):
        query_vec = embed_single(question)
        query_vec = np.array([query_vec]).astype("float32")

        results = self.store.search(query_vec, k=k)

        return results