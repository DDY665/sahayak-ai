from __future__ import annotations

import re


def _trim_text(value: object) -> str:
    return str(value or "").strip()


def _normalize_items(items) -> list[dict]:
    if not isinstance(items, list):
        return []
    normalized: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        normalized.append(item)
    return normalized


def _normalize_items_limited(items, max_items: int = 5) -> list[dict]:
    normalized = _normalize_items(items)
    deduped: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for item in normalized:
        label = _trim_text(item.get("label", "")).lower()
        value = _trim_text(item.get("value", "")).lower()
        if not label and not value:
            continue
        key = (label, value)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
        if len(deduped) >= max_items:
            break
    return deduped


def _point_category(item: dict) -> str:
    label = _trim_text(item.get("label", "")).lower()
    value = _trim_text(item.get("value", "")).lower()
    note = _trim_text(item.get("note", "")).lower()
    blob = f"{label} {value} {note}"

    deadline_terms = ["deadline", "due", "last date", "time limit", "डेडलाइन",
                      "अंतिम तिथि", "समय-सीमा", "गडువ", "గడువు", "చివరి తేదీ"]
    diagnostic_terms = ["diagnostic", "finding", "result", "test", "hemoglobin",
                        "wbc", "rbc", "platelet", "hba1c", "glucose", "creatinine",
                        "bilirubin", "cholesterol", "triglycerides", "tsh", "ecg",
                        "x-ray", "mri", "ultrasound", "డायग्नोस्टिक", "పరీక్ష", "నిర్ధారణ"]
    symptom_terms = ["symptom", "fever", "cough", "pain", "vomiting", "fatigue",
                     "weakness", "headache", "swelling", "infection", "inflammation",
                     "लक्षण", "లక్షణ"]
    finance_terms = ["amount", "emi", "interest", "penalty", "outstanding", "dues",
                     "payment", "financial", "राशि", "वित्तीय", "మొత్తం", "ఆర్థిక"]
    eligibility_terms = ["eligibility", "rule", "criteria", "required document",
                         "पात्रता", "नियम", "అర్హత", "నియమ"]

    if any(term in blob for term in deadline_terms):
        return "deadline"
    if any(term in blob for term in diagnostic_terms):
        return "diagnostic"
    if any(term in blob for term in symptom_terms):
        return "symptom"
    if any(term in blob for term in finance_terms):
        return "finance"
    if any(term in blob for term in eligibility_terms):
        return "eligibility"
    return "other"


def _normalize_point_label(item: dict, defaults: dict) -> dict:
    category = _point_category(item)
    if category == "deadline":
        item["label"] = defaults["deadline_label"]
    elif category == "diagnostic":
        item["label"] = defaults["diagnostic_label"]
    elif category == "symptom":
        item["label"] = defaults["symptom_label"]
    elif category == "finance" and _trim_text(item.get("label", "")) == "":
        item["label"] = defaults["amount_label"]
    elif category in {"other", "eligibility"} and _trim_text(item.get("label", "")) == "":
        item["label"] = defaults["reference_id_label"]
    return item


def _prioritize_points(points: list[dict], defaults: dict, max_items: int = 5) -> list[dict]:
    priority = {"deadline": 0, "diagnostic": 1, "symptom": 2, "finance": 3, "eligibility": 4, "other": 5}
    enriched = [_normalize_point_label(dict(item or {}), defaults) for item in points]
    deduped = _normalize_items_limited(enriched, max_items=20)
    sorted_points = sorted(
        deduped,
        key=lambda item: (
            priority.get(_point_category(item), 9),
            _trim_text(item.get("label", "")).lower(),
            _trim_text(item.get("value", "")).lower(),
        ),
    )
    return sorted_points[:max_items]
