from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = "test-key"
    database_url: str = "sqlite:///./rag.db"
    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    chat_model: str = "gpt-4o-mini"
    top_k: int = 4
    chunk_size: int = 200
    chunk_overlap: int = 50
    rate_limit_requests: int = 30
    rate_limit_window_seconds: int = 60

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
