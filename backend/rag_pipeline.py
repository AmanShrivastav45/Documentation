import hashlib
import math

EMBEDDING_DIM = 16


def mock_embed(text):
    """Deterministic pseudo-embedding: hashes the text into a fixed-size
    vector, so identical text always yields an identical vector. Swap for
    a real embeddings API call when moving beyond scaffolding."""
    vector = []
    for i in range(EMBEDDING_DIM):
        digest = hashlib.sha256(f"{i}:{text}".encode("utf-8")).hexdigest()
        vector.append(int(digest[:8], 16) / 0xFFFFFFFF)
    return vector


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class VectorStore:
    """In-memory scaffold vector store. Swap for Chroma/pgvector for
    production use without changing the retrieve_top_k interface."""

    def __init__(self):
        self._records = []

    def clear(self):
        self._records = []

    def add(self, record, embedding):
        self._records.append({**record, "embedding": embedding})

    def all(self):
        return list(self._records)

    def retrieve_top_k(self, query_text, k=3):
        query_vec = mock_embed(query_text)
        scored = [
            (cosine_similarity(query_vec, r["embedding"]), r) for r in self._records
        ]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [r for _, r in scored[:k]]


def mock_llm_answer(question, context_chunks):
    """Scaffold LLM call: templates an answer from retrieved chunk content.
    Replace with a real LLM client call for production use."""
    if not context_chunks:
        return "I couldn't find any relevant documentation for that question."
    snippets = "\n\n".join(
        f"- **{c['heading'] or c['file_path']}**: {' '.join(c['content'].split())[:200]}"
        for c in context_chunks
    )
    return (
        f'Based on the documentation, here\'s what I found regarding '
        f'"{question}":\n\n{snippets}'
    )
