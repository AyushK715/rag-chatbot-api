from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import auth, chat, documents
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="RAG Chatbot API",
    description="Retrieval-Augmented Generation service: upload documents, ask grounded questions.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}
