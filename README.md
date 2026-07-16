# RAG Chatbot API

A production-style **Retrieval-Augmented Generation (RAG)** service built with **FastAPI**, **PostgreSQL + pgvector**, and the **OpenAI API**. Upload documents, ask questions, and get grounded answers with source citations.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![Tests](https://img.shields.io/badge/tests-pytest-green)

## Architecture

```
                 ┌──────────────────────────────────────────────┐
                 │                  FastAPI                     │
                 │                                              │
  POST /documents ──► Chunker ──► OpenAI Embeddings ──► pgvector
                 │                                              │
  POST /chat ──────► Embed query ──► Similarity search ─────────┤
                 │        │                                     │
                 │        ▼                                     │
                 │   Top-k chunks + question ──► GPT-4o-mini    │
                 │        │                                     │
  Answer + sources ◄──────┘                                     │
                 └──────────────────────────────────────────────┘
```

## Features

- **Document ingestion** — upload raw text or files; automatic chunking with overlap for context continuity
- **Vector search** — cosine similarity over pgvector with an IVFFlat index
- **Grounded answers** — the LLM answers *only* from retrieved context and cites its sources; says "I don't know" instead of hallucinating
- **Streaming-ready design** — clean service layer separation (API / services / core)
- **JWT authentication** — register/login, protected endpoints
- **Rate limiting** — simple in-memory sliding-window limiter per user
- **Fully tested** — Pytest suite with mocked OpenAI calls (no API key needed to run tests)
- **Dockerized** — one command spins up API + PostgreSQL/pgvector

## Quickstart

```bash
git clone https://github.com/ayushkumar715/rag-chatbot-api.git
cd rag-chatbot-api
cp .env.example .env          # add your OPENAI_API_KEY
docker compose up --build
```

API docs: http://localhost:8000/docs

### Example usage

```bash
# 1. Register + get a token
curl -X POST localhost:8000/auth/register -H 'Content-Type: application/json' \
  -d '{"email": "me@example.com", "password": "secret123"}'
TOKEN=$(curl -s -X POST localhost:8000/auth/login -H 'Content-Type: application/json' \
  -d '{"email": "me@example.com", "password": "secret123"}' | jq -r .access_token)

# 2. Ingest a document
curl -X POST localhost:8000/documents -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title": "Company FAQ", "content": "Our refund policy allows returns within 30 days..."}'

# 3. Ask a question
curl -X POST localhost:8000/chat -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"question": "What is the refund window?"}'
# → {"answer": "Returns are allowed within 30 days...", "sources": [{"title": "Company FAQ", ...}]}
```

## Running tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -v
```

All OpenAI calls are mocked in tests — no API key or database required (SQLite + fake embeddings are used).

## Project structure

```
app/
├── main.py              # FastAPI app, routers, startup
├── core/
│   ├── config.py        # Pydantic settings from env
│   ├── security.py      # JWT creation/validation, password hashing
│   └── rate_limit.py    # Sliding-window rate limiter
├── api/
│   ├── auth.py          # /auth/register, /auth/login
│   ├── documents.py     # /documents CRUD
│   └── chat.py          # /chat RAG endpoint
└── services/
    ├── chunking.py      # Text splitter with overlap
    ├── embeddings.py    # OpenAI embedding client (batched)
    ├── retrieval.py     # pgvector similarity search
    └── generation.py    # Prompt assembly + chat completion
tests/                   # Pytest suite (mocked LLM)
```

## Key design decisions

- **Chunk overlap (200/50 tokens)** — prevents answers from being split across chunk boundaries
- **Grounding prompt** — system prompt forbids answering outside the retrieved context, reducing hallucination
- **Batched embeddings** — documents are embedded in batches of 64 to cut API round-trips
- **Idempotent ingestion** — re-uploading the same content hash skips re-embedding (saves cost)

## Tech

Python 3.11 · FastAPI · SQLAlchemy 2.0 · PostgreSQL 16 + pgvector · OpenAI API · Docker · Pytest

---

*Built by [Ayush Kumar](https://linkedin.com/in/ayushkumar715) — Backend Engineer (Python)*
