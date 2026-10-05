from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import List, Optional

from langchain_core.documents import Document


class RAGRetrievalMixin:
    def _tokenize(self, text: str) -> list[str]:
        return [token for token in re.split(r"\W+", text.lower()) if token]

    def _keyword_search(
        self,
        question: str,
        top_k: int,
        documents: list[Document] | None = None,
    ) -> list[Document]:
        """Keyword search over provided documents (or session docs if not specified)."""
        query_terms = self._tokenize(question)
        if not query_terms:
            return []
        terms = Counter(query_terms)
        source_docs = documents if documents is not None else []
        scored: list[tuple[int, Document]] = []
        for doc in source_docs:
            haystack = f"{doc.metadata.get('source', '')} {doc.page_content}".lower()
            score = sum(haystack.count(term) * weight for term, weight in terms.items())
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]

    def _rerank_documents(self, question: str, docs: list[Document], top_k: int) -> list[Document]:
        query_terms = set(self._tokenize(question))
        if not docs:
            return []
        scored: list[tuple[float, Document]] = []
        for idx, doc in enumerate(docs):
            text = f"{doc.metadata.get('source', '')} {doc.page_content}".lower()
            doc_terms = set(self._tokenize(text))
            overlap_ratio = len(query_terms.intersection(doc_terms)) / max(1, len(query_terms))
            phrase_boost = 0.25 if question.lower() in text else 0.0
            order_bonus = max(0.0, 0.2 - idx * 0.01)
            scored.append((overlap_ratio + phrase_boost + order_bonus, doc))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]

    def _retrieval_confidence(self, question: str, docs: list[Document]) -> float:
        query_terms = set(self._tokenize(question))
        if not query_terms or not docs:
            return 0.0
        overlap_terms: set[str] = set()
        for doc in docs:
            text_terms = set(self._tokenize(f"{doc.metadata.get('source', '')} {doc.page_content}"))
            overlap_terms.update(query_terms.intersection(text_terms))
        return len(overlap_terms) / max(1, len(query_terms))

    def _should_bypass_confidence_gate(self, question: str) -> bool:
        q = str(question or "").lower()
        if not q:
            return False
        guided_markers = (
            "concise summary", "top takeaways", "important dates", "deadlines",
            "financial impact", "eligibility", "medical details", "key points",
            "त्वरित सारांश", "मुख्य बातें", "महत्वपूर्ण तिथियां", "समय-सीमाएं",
            "वित्तीय प्रभाव", "पात्रता", "चिकित्सीय विवरण",
            "త్వరిత సారాంశం", "ముఖ్య విషయాలు", "ముఖ్య తేదీలు",
            "గడువులు", "ఆర్థిక ప్రభావం", "అర్హత", "వైద్య వివరాలు",
        )
        return any(marker in q for marker in guided_markers)

    def _expand_query_with_history(self, question: str, history: list[dict] | None = None) -> str:
        """Enrich likely follow-up queries with previous assistant response context."""
        if not history:
            return question
        followup_keywords = {"first", "second", "third", "that", "it", "this", "more",
                             "explain", "elaborate", "why", "what about", "those"}
        lower_q = question.lower()
        if not any(keyword in lower_q for keyword in followup_keywords):
            return question
        last_assistant = None
        for msg in reversed(history):
            if str(msg.get("role", "")).lower() == "assistant":
                last_assistant = str(msg.get("content", "")).strip()
                if last_assistant:
                    break
        if not last_assistant:
            return question
        return f"{question}. Previous answer context: {last_assistant[:400]}"

    def _hybrid_retrieve(
        self,
        question: str,
        top_k: int,
        history: list[dict] | None = None,
        document_name: str | None = None,
        user_id: str | None = None,
        chat_id: str | None = None,
    ) -> list[Document]:
        # Resolve the session-scoped vector store
        store = None
        if user_id and chat_id:
            store = self._get_or_load_session_store(user_id, chat_id)
        
        if store is None:
            return []

        search_query = self._expand_query_with_history(question, history)
        candidate_k = max(10, top_k * 4)
        dense_k = max(8, candidate_k)

        retriever = store.as_retriever(search_kwargs={"k": dense_k})
        dense_docs = retriever.invoke(search_query)

        # Get all docs in this session for keyword search
        session_docs = self._all_documents_for_session(user_id, chat_id) if user_id and chat_id else []
        keyword_docs = self._keyword_search(search_query, candidate_k, documents=session_docs)

        doc_name_lower = Path(document_name).name.lower() if document_name else None

        merged: list[Document] = []
        seen: set[tuple[str, str]] = set()

        for doc in list(dense_docs) + list(keyword_docs):
            source = str(doc.metadata.get("source", "unknown")).lower()
            source_basename = Path(source).name.lower()

            # STRICT DOCUMENT FILTERING — no cross-document contamination
            if doc_name_lower and source_basename != doc_name_lower:
                continue

            key = (source_basename, doc.page_content)
            if key in seen:
                continue
            seen.add(key)
            merged.append(doc)
            if len(merged) >= candidate_k:
                break

        return self._rerank_documents(question, merged, top_k)
