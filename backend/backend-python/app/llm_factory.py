from __future__ import annotations

import os

from langchain_groq import ChatGroq


def _groq_api_key_for_purpose(purpose: str) -> str:
    purpose_key = str(purpose or "chat").strip().lower()
    if purpose_key == "summary":
        return (
            os.getenv("GROQ_SUMMARY_API_KEY", "").strip()
            or os.getenv("GROQ_ANALYSIS_API_KEY", "").strip()
            or os.getenv("GROQ_API_KEY", "").strip()
        )
    return (
        os.getenv("GROQ_CHAT_API_KEY", "").strip()
        or os.getenv("GROQ_CONVERSATION_API_KEY", "").strip()
        or os.getenv("GROQ_API_KEY", "").strip()
    )


def build_llm_from_env(purpose: str = "chat") -> ChatGroq:
    api_key = _groq_api_key_for_purpose(purpose)
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    return ChatGroq(model=model, temperature=0, groq_api_key=api_key or "gsk_placeholder_pending_config")
