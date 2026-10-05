from __future__ import annotations

from .store import RAGStoreMixin
from .retrieval import RAGRetrievalMixin
from .clarification import RAGClarificationMixin
from .answering import RAGAnsweringMixin
from .document_analysis import RAGDocumentAnalysisMixin


class RAGEngine(
    RAGStoreMixin,
    RAGRetrievalMixin,
    RAGClarificationMixin,
    RAGAnsweringMixin,
    RAGDocumentAnalysisMixin,
):
    """Full RAG engine composed from focused mixin classes."""
