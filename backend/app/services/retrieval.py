import hashlib, math, re
from collections import Counter

DIM = 128

def embed(text: str) -> list[float]:
    # Deterministic feature-hash vector for local demos only; replace with a real embedding provider for semantic retrieval.
    vec = [0.0] * DIM
    tokens = re.findall(r"[a-z0-9_]+", text.lower())
    for token in tokens:
        digest = hashlib.sha256(token.encode()).digest()
        idx = int.from_bytes(digest[:4], "big") % DIM
        vec[idx] += 1.0 if digest[4] % 2 else -1.0
    norm = math.sqrt(sum(v*v for v in vec)) or 1.0
    return [v / norm for v in vec]

def cosine(a: list[float], b: list[float]) -> float:
    return sum(x*y for x, y in zip(a, b))

def lexical_score(query: str, text: str) -> float:
    q = Counter(re.findall(r"[a-z0-9_]+", query.lower()))
    d = Counter(re.findall(r"[a-z0-9_]+", text.lower()))
    if not q: return 0.0
    return sum(min(count, d[token]) for token, count in q.items()) / (sum(q.values()) or 1)

def split_chunks(text: str, size: int = 900, overlap: int = 120) -> list[str]:
    words = text.split()
    if not words: return []
    chunks, start = [], 0
    while start < len(words):
        end = min(len(words), start + size)
        chunks.append(" ".join(words[start:end]))
        if end == len(words): break
        start = max(start + 1, end - overlap)
    return chunks

def retrieve(query: str, documents: list, top_k: int = 5) -> list[dict]:
    qv = embed(query)
    results = []
    for doc in documents:
        for index, chunk in enumerate(doc.chunks or []):
            vec_score = cosine(qv, embed(chunk))
            lex_score = lexical_score(query, chunk)
            score = 0.55 * vec_score + 0.45 * lex_score
            results.append({"document_id": doc.id, "filename": doc.filename,
                            "chunk_index": index, "text": chunk,
                            "vector_score": round(vec_score, 4),
                            "lexical_score": round(lex_score, 4),
                            "score": round(score, 4)})
    return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
