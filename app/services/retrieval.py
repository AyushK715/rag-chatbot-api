from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Chunk, Document


def similar_chunks(db: Session, query_embedding: list[float], owner_email: str) -> list[Chunk]:
    """Return the top-k most similar chunks for this user via cosine distance."""
    settings = get_settings()
    stmt = (
        select(Chunk)
        .join(Document)
        .where(Document.owner_email == owner_email)
        .order_by(Chunk.embedding.cosine_distance(query_embedding))
        .limit(settings.top_k)
    )
    return list(db.scalars(stmt))
