from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.rate_limit import rate_limit
from app.db import get_db
from app.schemas import ChatRequest, ChatResponse, SourceInfo
from app.services.embeddings import embed_query
from app.services.generation import generate_answer
from app.services.retrieval import similar_chunks

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    email: str = Depends(rate_limit),
    db: Session = Depends(get_db),
) -> ChatResponse:
    query_vector = embed_query(payload.question)
    chunks = similar_chunks(db, query_vector, owner_email=email)

    if not chunks:
        return ChatResponse(
            answer="I don't know based on the provided documents. Try uploading some documents first.",
            sources=[],
        )

    answer = generate_answer(payload.question, chunks)
    sources = [
        SourceInfo(
            document_id=chunk.document_id,
            title=chunk.document.title,
            snippet=chunk.text[:200],
        )
        for chunk in chunks
    ]
    return ChatResponse(answer=answer, sources=sources)
