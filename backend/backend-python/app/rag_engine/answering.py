from __future__ import annotations

import logging
import os
from typing import Iterable

logger = logging.getLogger(__name__)


def _is_rate_limit_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return any(term in message for term in [
        "ratelimit", "rate limit", "429", "tpm", "rpm", "quota",
        "resource_exhausted", "rate_limit_exceeded"
    ])


class RAGAnsweringMixin:
    def build_answer(
        self,
        question: str,
        top_k: int = 4,
        language: str = "English",
        history: list[dict] | None = None,
        document_name: str | None = None,
        user_id: str | None = None,
        chat_id: str | None = None,
    ) -> tuple[str, list[dict]]:
        if self._is_ambiguous_question(question):
            if self._has_recent_clarification_prompt(history):
                question = self._default_scope_question(language)
            else:
                return self._build_clarifying_question(language), []

        if not question.strip():
            return self._build_clarifying_question(language), []

        docs = self._hybrid_retrieve(
            question, top_k, history,
            document_name=document_name,
            user_id=user_id,
            chat_id=chat_id,
        )
        if not docs:
            return "I could not find this in the uploaded documents.", []

        confidence = self._retrieval_confidence(question, docs)
        threshold = float(os.getenv("MIN_RETRIEVAL_CONFIDENCE", "0.0"))
        if confidence < threshold and not self._should_bypass_confidence_gate(question):
            return (
                "I could not find this in the uploaded documents with enough confidence. "
                "Try asking with exact terms from the document.",
                [],
            )

        context = "\n\n".join([f"[{d.metadata.get('source', 'unknown')}] {d.page_content}" for d in docs])
        chain = self.prompt | self.chat_llm
        try:
            response = chain.invoke(self._build_chat_prompt_inputs(question, context, language, history))
        except Exception as exc:
            logger.error("Answer generation failed: %s", exc, exc_info=True)
            if _is_rate_limit_error(exc):
                return ("The AI service is temporarily rate-limited. Please try again in a few minutes.", [])
            return (f"I could not generate an answer right now. Please try again shortly. (Error: {exc})", [])

        answer_text = getattr(response, "content", str(response))
        citations = [
            {"source": d.metadata.get("source", "unknown"),
             "snippet": d.page_content[:200] + ("..." if len(d.page_content) > 200 else "")}
            for d in docs
        ]
        return answer_text, citations

    def stream_answer(
        self,
        question: str,
        top_k: int = 4,
        language: str = "English",
        history: list[dict] | None = None,
        document_name: str | None = None,
        user_id: str | None = None,
        chat_id: str | None = None,
    ) -> tuple[Iterable[str], list[dict]]:
        if self._is_ambiguous_question(question):
            if self._has_recent_clarification_prompt(history):
                question = self._default_scope_question(language)
            else:
                return iter([self._build_clarifying_question(language)]), []

        if not question.strip():
            return iter([self._build_clarifying_question(language)]), []

        docs = self._hybrid_retrieve(
            question, top_k, history,
            document_name=document_name,
            user_id=user_id,
            chat_id=chat_id,
        )
        if not docs:
            return iter(["I could not find this in the uploaded documents."]), []

        confidence = self._retrieval_confidence(question, docs)
        threshold = float(os.getenv("MIN_RETRIEVAL_CONFIDENCE", "0.0"))
        if confidence < threshold and not self._should_bypass_confidence_gate(question):
            return iter([
                "I could not find this in the uploaded documents with enough confidence. "
                "Try asking with exact terms from the document."
            ]), []

        context = "\n\n".join([f"[{d.metadata.get('source', 'unknown')}] {d.page_content}" for d in docs])
        citations = [
            {"source": d.metadata.get("source", "unknown"),
             "snippet": d.page_content[:200] + ("..." if len(d.page_content) > 200 else "")}
            for d in docs
        ]
        chain = self.prompt | self.chat_llm
        try:
            stream = chain.stream(self._build_chat_prompt_inputs(question, context, language, history))
        except Exception as exc:
            logger.error("Stream setup failed: %s", exc, exc_info=True)
            if _is_rate_limit_error(exc):
                return iter(["The AI service is temporarily rate-limited. Please try again in a few minutes."]), []
            return iter([f"I could not generate an answer right now. (Error: {exc})"]), []

        def generator() -> Iterable[str]:
            try:
                for chunk in stream:
                    token = getattr(chunk, "content", None)
                    if token:
                        yield token
            except Exception as exc:
                logger.error("Stream generation failed: %s", exc, exc_info=True)
                if _is_rate_limit_error(exc):
                    yield "The AI service is temporarily rate-limited. Please try again in a few minutes."
                else:
                    yield f"I could not generate an answer right now. (Error: {exc})"

        return generator(), citations
