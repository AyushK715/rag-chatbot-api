from openai import OpenAI

from app.core.config import get_settings

_BATCH_SIZE = 64


def _client() -> OpenAI:
    return OpenAI(api_key=get_settings().openai_api_key)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed texts in batches to reduce API round-trips."""
    settings = get_settings()
    client = _client()
    vectors: list[list[float]] = []
    for i in range(0, len(texts), _BATCH_SIZE):
        batch = texts[i : i + _BATCH_SIZE]
        response = client.embeddings.create(model=settings.embedding_model, input=batch)
        vectors.extend(item.embedding for item in response.data)
    return vectors


def embed_query(question: str) -> list[float]:
    return embed_texts([question])[0]
