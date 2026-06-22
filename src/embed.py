from sentence_transformers import SentenceTransformer

# Good local model (fast + strong)
model = SentenceTransformer("BAAI/bge-small-en")


def get_embeddings(texts):
    """
    Convert list of texts → vectors
    """
    embeddings = model.encode(
        texts,
        normalize_embeddings=True
    )
    return embeddings


def embed_single(text):
    return get_embeddings([text])[0]