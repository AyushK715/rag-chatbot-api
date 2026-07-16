import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rate_limit import rate_limit
from app.db import get_db
from app.models import Chunk, Document
from app.schemas import DocumentCreate, DocumentResponse
from app.services.chunking import chunk_text
from app.services.embeddings import embed_texts

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    payload: DocumentCreate,
    email: str = Depends(rate_limit),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    settings = get_settings()
    content_hash = hashlib.sha256(payload.content.encode()).hexdigest()

    # Idempotent ingestion: skip re-embedding identical content
    existing = db.scalar(
        select(Document).where(
            Document.owner_email == email, Document.content_hash == content_hash
        )
    )
    if existing:
        return DocumentResponse(
            id=existing.id,
            title=existing.title,
            chunk_count=len(existing.chunks),
            deduplicated=True,
        )

    chunks = chunk_text(payload.content, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        raise HTTPException(status_code=422, detail="Document has no content to index")

    embeddings = embed_texts(chunks)

    document = Document(owner_email=email, title=payload.title, content_hash=content_hash)
    db.add(document)
    db.flush()
    for position, (text, vector) in enumerate(zip(chunks, embeddings)):
        db.add(Chunk(document_id=document.id, position=position, text=text, embedding=vector))
    db.commit()

    return DocumentResponse(id=document.id, title=document.title, chunk_count=len(chunks))


@router.get("")
def list_documents(email: str = Depends(rate_limit), db: Session = Depends(get_db)) -> list[dict]:
    docs = db.scalars(select(Document).where(Document.owner_email == email)).all()
    return [{"id": d.id, "title": d.title, "created_at": d.created_at.isoformat()} for d in docs]


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int, email: str = Depends(rate_limit), db: Session = Depends(get_db)
) -> None:
    doc = db.get(Document, document_id)
    if not doc or doc.owner_email != email:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
