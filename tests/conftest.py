"""Test fixtures: in-memory SQLite + fully mocked OpenAI calls (no API key needed)."""
import hashlib
import os
from unittest.mock import patch

import pytest

os.environ["DATABASE_URL"] = "sqlite://"  # in-memory
os.environ["OPENAI_API_KEY"] = "test-key"

from fastapi.testclient import TestClient  # noqa: E402


def fake_vector(text: str, dim: int = 1536) -> list[float]:
    """Deterministic pseudo-embedding derived from the text hash."""
    digest = hashlib.sha256(text.encode()).digest()
    return [(digest[i % len(digest)] / 255.0) for i in range(dim)]


def _sqlite_similar_chunks(db, query_embedding, owner_email):
    from sqlalchemy import select

    from app.models import Chunk, Document

    stmt = (
        select(Chunk)
        .join(Document)
        .where(Document.owner_email == owner_email)
        .limit(4)
    )
    return list(db.scalars(stmt))


@pytest.fixture()
def client():
    # SQLite has no pgvector: store embeddings as None and patch retrieval too.
    with (
        patch("app.api.documents.embed_texts", side_effect=lambda texts: [None for _ in texts]),
        patch("app.api.chat.embed_query", side_effect=lambda q: fake_vector(q)),
        patch("app.api.chat.similar_chunks", side_effect=_sqlite_similar_chunks),
        patch("app.api.chat.generate_answer", return_value="Mocked grounded answer."),
    ):
        from app.db import engine
        from app.models import Base

        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        from app.main import app

        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture()
def auth_headers(client):
    client.post("/auth/register", json={"email": "test@example.com", "password": "secret123"})
    response = client.post(
        "/auth/login", json={"email": "test@example.com", "password": "secret123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
