from __future__ import annotations

import re

from .item_utils import _trim_text


def _extract_subject_name(text: str) -> str:
    source = str(text or "")
    explicit = re.search(
        r"\b(?:patient\s*name|name)\s*[:\-]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})",
        source,
        re.IGNORECASE,
    )
    if explicit:
        return _trim_text(explicit.group(1))

    title_name = re.search(
        r"\b(?:Mr|Mrs|Ms|Miss|Dr)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}",
        source,
    )
    if title_name:
        return _trim_text(title_name.group(0))
    return ""


def _summary_looks_noisy(summary: str) -> bool:
    s = _trim_text(summary)
    if not s:
        return True
    numbers = len(re.findall(r"\d", s))
    alpha = len(re.findall(r"[A-Za-z]", s))
    if len(s) > 260 and numbers > max(35, alpha // 2):
        return True
    if len(s.split()) > 45 and s.count(".") <= 1:
        return True
    if s.count("/") >= 6 or s.count("%") >= 6:
        return True
    if len(re.findall(r"\b\d+(?:\.\d+)?\b", s)) >= 18:
        return True
    return False


def _summary_is_generic(summary: str) -> bool:
    s = _trim_text(summary).lower()
    if not s:
        return True
    generic_markers = [
        "this document contains important information",
        "this document contains uploaded content",
        "it explains the main subject",
        "details that matter most",
        "follow-up questions",
        "important points",
        "can be explained further",
        "document uploaded successfully",
        "now you can ask questions",
        "can now ask questions",
    ]
    return any(marker in s for marker in generic_markers)
