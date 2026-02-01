from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


# Chat
class ChatRequest(BaseModel):
    conversation_id: Optional[UUID] = None
    message: str


class ChatResponse(BaseModel):
    conversation_id: UUID
    response: str


# Card Generation
class GenerateRequest(BaseModel):
    conversation_id: UUID


class CardCandidate(BaseModel):
    card_type: str  # 'vocab', 'cloze', 'rewrite'
    front: str
    back: str


class GenerateResponse(BaseModel):
    candidates: list[CardCandidate]


# Card Approval
class ApproveRequest(BaseModel):
    conversation_id: UUID
    cards: list[CardCandidate]


class CardOut(BaseModel):
    id: UUID
    card_type: str
    front: str
    back: str
    next_review: date
    created_at: datetime

    class Config:
        from_attributes = True


class ApproveResponse(BaseModel):
    created: list[CardOut]


# Health
class HealthResponse(BaseModel):
    status: str
    database: str


# Word Lookup
class LookupRequest(BaseModel):
    word: str
    context: Optional[str] = None  # 元の文（文脈）


class LookupResponse(BaseModel):
    word: str
    meaning: str
    example: Optional[str] = None
    pronunciation: Optional[str] = None


# Quick Card Creation (単語から直接カード作成)
class QuickCardRequest(BaseModel):
    word: str
    meaning: str
    context: Optional[str] = None
    card_type: str = "vocab"  # vocab, cloze


class CardUpdate(BaseModel):
    front: Optional[str] = None
    back: Optional[str] = None
    card_type: Optional[str] = None
