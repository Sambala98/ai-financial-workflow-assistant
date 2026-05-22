from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def generate_embedding(text: str) -> list[float]:
    if not text or not text.strip():
        return []

    embedding = model.encode(text)
    return embedding.tolist()