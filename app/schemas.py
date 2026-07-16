from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1)


class DocumentResponse(BaseModel):
    id: int
    title: str
    chunk_count: int
    deduplicated: bool = False


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class SourceInfo(BaseModel):
    document_id: int
    title: str
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]
