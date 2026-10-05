from __future__ import annotations

import re

from .item_utils import _trim_text, _normalize_items_limited


def _enrich_important_dates(items: list[dict], source: str, defaults: dict) -> list[dict]:
    enriched: list[dict] = []
    text = str(source or "")
    compact = re.sub(r"\s+", " ", text)

    generic_labels = {
        str(defaults.get("important_date_label", "")).strip().lower(),
        "important date", "date", "महत्वपूर्ण तिथि", "तारीख", "ముఖ్యమైన తేదీ", "తేదీ",
    }
    generic_notes = {str(defaults.get("important_date_note", "")).strip().lower(), ""}

    for raw in items:
        item = dict(raw or {})
        value = _trim_text(item.get("value", ""))
        label = _trim_text(item.get("label", "")) or defaults["important_date_label"]
        note = _trim_text(item.get("note", ""))

        if value:
            m = re.search(re.escape(value), compact, re.IGNORECASE)
            if m:
                start = max(0, m.start() - 70)
                end = min(len(compact), m.end() + 90)
                window = compact[start:end]
                context = re.sub(r"\s+", " ", window).strip(" .,-")
                if context:
                    if label.lower() in generic_labels:
                        lead = re.sub(r"[^A-Za-z\u0900-\u097F\u0C00-\u0C7F\s]", " ", context)
                        lead = " ".join(lead.split())
                        words = [
                            w for w in lead.split()
                            if w.lower() not in {"the", "and", "of", "for", "to", "on", "in", "with", "at"}
                        ]
                        if words:
                            label = " ".join(words[:4]).strip().title()
                    if note.lower() in generic_notes:
                        note = context

        item["label"] = label or defaults["important_date_label"]
        item["value"] = value
        item["note"] = note or defaults["important_date_note"]
        enriched.append(item)

    return _normalize_items_limited(enriched, max_items=3)


def _infer_doc_type(
    doc_type: str,
    important_dates: list[dict],
    important_points: list[dict],
    highlights: list[dict],
    preview: str,
    medical_conclusion: str,
) -> str:
    normalized = str(doc_type or "unknown").strip().lower()
    if normalized in {"medical", "bank", "government"}:
        return normalized

    if medical_conclusion:
        return "medical"

    preview_l = str(preview or "").lower()

    for item in important_points:
        label = str(item.get("label", "")).lower()
        value = str(item.get("value", "")).lower()
        if "medical" in label or "medical" in value or "diagnosis" in value or "blood pressure" in value:
            return "medical"
        if any(k in f"{label} {value}" for k in ["bank", "loan", "emi", "interest", "statement", "amount", "financial"]):
            return "bank"
        if any(k in f"{label} {value}" for k in ["government", "scheme", "eligibility", "deadline", "benefit", "application"]):
            return "government"

    for item in highlights:
        name = str(item.get("name", "")).lower()
        value = str(item.get("value", "")).lower()
        note = str(item.get("note", "")).lower()
        blob = f"{name} {value} {note}"
        if any(k in blob for k in ["medical", "diagnosis", "patient", "hemoglobin", "wbc", "rbc",
                                    "platelet", "hba1c", "glucose", "creatinine", "bilirubin",
                                    "x-ray", "mri", "ultrasound", "ecg"]):
            return "medical"
        if any(k in blob for k in ["loan", "emi", "interest", "statement", "bank", "financial", "penalty", "amount"]):
            return "bank"
        if any(k in blob for k in ["scheme", "eligibility", "government", "deadline", "benefit", "application", "notice"]):
            return "government"

    if any(k in preview_l for k in ["diagnosis", "patient", "lab", "hemoglobin", "wbc", "rbc", "platelet", "blood", "hba1c", "glucose"]):
        return "medical"
    if any(k in preview_l for k in ["loan", "emi", "interest", "statement", "bank", "account", "outstanding", "penalty"]):
        return "bank"
    if any(k in preview_l for k in ["government", "scheme", "eligibility", "benefit", "application", "deadline", "notice"]):
        return "government"

    if important_dates and not important_points:
        return "government"

    return "unknown"
