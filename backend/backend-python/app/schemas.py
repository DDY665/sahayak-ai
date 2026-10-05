from pydantic import BaseModel, Field
from typing import Optional, List


class HistoryMessage(BaseModel):
    role: str
    content: str


class AskRequest(BaseModel):
    question: str
    language: str = "English"
    documentName: Optional[str] = None
    document_name: Optional[str] = None
    conversationId: Optional[str] = None
    chat_id: Optional[str] = None
    userId: Optional[str] = None
    user_id: Optional[str] = None
    history: List[HistoryMessage] = Field(default_factory=list)

    def get_document_name(self) -> Optional[str]:
        return self.documentName or self.document_name

    def get_conversation_id(self) -> Optional[str]:
        return self.conversationId or self.chat_id

    def get_user_id(self) -> Optional[str]:
        return self.userId or self.user_id


class Citation(BaseModel):
    source: str
    snippet: str


class AskResponse(BaseModel):
    id: Optional[str] = None
    conversationId: Optional[str] = None
    question: str
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    latencyMs: Optional[float] = None
    createdAt: Optional[str] = None


class DocumentInfo(BaseModel):
    filename: str
    chunks: int
