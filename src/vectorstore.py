import faiss
import numpy as np
import os


class VectorStore:
    def __init__(self, dim, index_path="storage/faiss_index/index.faiss"):
        self.dim = dim
        self.index_path = index_path

        self.index = faiss.IndexFlatIP(dim)  # cosine similarity (if normalized)
        self.chunks = []

        # load if exists
        if os.path.exists(index_path):
            self.load()

    def add(self, embeddings, texts):
        """
        Store embeddings + corresponding text chunks
        """
        embeddings = np.array(embeddings).astype("float32")

        self.index.add(embeddings)
        self.chunks.extend(texts)

    def search(self, query_embedding, k=5):
        """
        Search similar chunks
        """
        query_embedding = np.array(query_embedding).astype("float32")

        scores, indices = self.index.search(query_embedding, k)

        results = []
        for idx in indices[0]:
            if idx < len(self.chunks):
                results.append(self.chunks[idx])

        return results

    def save(self):
        faiss.write_index(self.index, self.index_path)

        # save chunks separately
        with open(self.index_path + ".txt", "w", encoding="utf-8") as f:
            for c in self.chunks:
                f.write(c.replace("\n", " ") + "\n")

    def load(self):
        self.index = faiss.read_index(self.index_path)

        # load chunks
        try:
            with open(self.index_path + ".txt", "r", encoding="utf-8") as f:
                self.chunks = [line.strip() for line in f.readlines()]
        except:
            self.chunks = []