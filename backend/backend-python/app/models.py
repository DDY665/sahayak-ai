from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

class CitationItem(BaseModel):
    source: Optional[str] = None
    snippet: Optional[str] = None

class UserModel(BaseModel):
    name: str
    email: str
    password: str
    createdAt: datetime = Field(default_factory=now_utc)
    updatedAt: datetime = Field(default_factory=now_utc)

class ConversationModel(BaseModel):
    userId: str
    title: str = "New Chat"
    documentName: Optional[str] = None
    language: str = "English"
    documentUploaded: bool = False
    chunksCount: str = "—"
    analysis: Optional[Dict[str, Any]] = None
    createdAt: datetime = Field(default_factory=now_utc)
    updatedAt: datetime = Field(default_factory=now_utc)

class ChatModel(BaseModel):
    userId: Optional[str] = None
    conversationId: Optional[str] = None
    question: str
    answer: str = ""
    latencyMs: Optional[float] = None
    retrievalCount: int = 0
    streamed: bool = False
    citations: List[CitationItem] = Field(default_factory=list)
    error: Optional[str] = None
    createdAt: datetime = Field(default_factory=now_utc)
    updatedAt: datetime = Field(default_factory=now_utc)
