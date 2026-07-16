"""Simple word-based text splitter with overlap.

Word-based chunking keeps the implementation dependency-light while
approximating token counts closely enough for retrieval purposes.
"""


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    step = chunk_size - overlap
    for start in range(0, len(words), step):
        window = words[start : start + chunk_size]
        chunks.append(" ".join(window))
        if start + chunk_size >= len(words):
            break
    return chunks
