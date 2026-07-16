from openai import OpenAI

from app.core.config import get_settings
from app.models import Chunk

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions using ONLY the provided context. "
    "If the context does not contain the answer, say \"I don't know based on the provided documents.\" "
    "Never invent information. Keep answers concise."
)


def build_context(chunks: list[Chunk]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[Source {i}: {chunk.document.title}]\n{chunk.text}")
    return "\n\n".join(parts)


def generate_answer(question: str, chunks: list[Chunk]) -> str:
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)
    context = build_context(chunks)
    response = client.chat.completions.create(
        model=settings.chat_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or ""
