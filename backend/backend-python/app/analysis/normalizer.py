from __future__ import annotations

from .defaults import _language_defaults
from .dates_enricher import _enrich_important_dates, _infer_doc_type
from .item_utils import _trim_text, _normalize_items, _normalize_items_limited, _prioritize_points
from .summary import _finalize_summary_with_context


def normalize_analysis(parsed: dict, preview: str, language: str = "English") -> dict:
    # Import here to avoid circular dep (fallback_analysis is in fallback.py)
    from .fallback import fallback_analysis

    defaults = _language_defaults(language)
    highlights = _normalize_items(parsed.get("highlights", []))
    important_dates = _normalize_items(parsed.get("important_dates", []))
    important_points = _normalize_items_limited(parsed.get("important_points", []), max_items=5)
    legacy_medical_details = _normalize_items(parsed.get("medical_details", []))
    legacy_important_details = _normalize_items(parsed.get("important_details", []))
    parsed_crux = _trim_text(parsed.get("crux", ""))
    parsed_summary = _trim_text(parsed.get("summary", ""))
    parsed_medical_conclusion = _trim_text(parsed.get("medical_conclusion", ""))
    doc_type = str(parsed.get("doc_type", "unknown") or "unknown").strip().lower()

    if not important_points:
        important_points = _normalize_items_limited(legacy_important_details, max_items=5)
    if not important_points and doc_type == "medical":
        important_points = _normalize_items_limited(legacy_medical_details, max_items=5)

    if (
        len(highlights) == 0
        and len(important_dates) == 0
        and len(important_points) == 0
        and not parsed_crux
        and not parsed_summary
        and not parsed_medical_conclusion
    ):
        fallback = fallback_analysis(preview, language=language)
        highlights = fallback.get("highlights", [])
        important_dates = fallback.get("important_dates", [])
        important_points = fallback.get("important_points", [])
        parsed_medical_conclusion = fallback.get("medical_conclusion", "")

    doc_type = _infer_doc_type(
        doc_type, important_dates, important_points, highlights, preview, parsed_medical_conclusion,
    )

    if doc_type != "medical":
        parsed_medical_conclusion = ""

    important_dates = _enrich_important_dates(important_dates, preview, defaults)
    parsed_summary = _finalize_summary_with_context(
        parsed_summary, doc_type, preview, language, important_dates, important_points,
    )

    # Ensure key time-bound info also appears in important points without flooding.
    for date_item in important_dates[:2]:
        if len(important_points) >= 5:
            break
        important_points.append({
            "label": defaults["deadline_label"],
            "value": _trim_text(date_item.get("value", "")),
            "note": _trim_text(date_item.get("note", "")) or defaults["deadline_note"],
        })

    important_points = _prioritize_points(important_points, defaults, max_items=5)

    return {
        "doc_type": doc_type,
        "doc_title": parsed.get("doc_title", defaults["doc_title"]),
        "crux": parsed_crux or defaults["crux"],
        "summary": parsed_summary or defaults["summary"],
        "medical_conclusion": parsed_medical_conclusion,
        "important_dates": important_dates,
        "important_points": important_points,
        "highlights": highlights,
    }
