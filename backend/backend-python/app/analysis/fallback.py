from __future__ import annotations

import re

from .defaults import _language_defaults
from .dates_enricher import _enrich_important_dates
from .item_utils import _trim_text, _prioritize_points
from .summary import _human_summary


def fallback_analysis(text: str, language: str = "English") -> dict:
    defaults = _language_defaults(language)
    source = str(text or "")
    highlights: list[dict] = []
    important_dates: list[dict] = []
    important_points: list[dict] = []

    compact = re.sub(r"\s+", " ", source).strip()
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", compact) if len(s.strip()) >= 25]
    inferred_crux = sentences[0] if sentences else defaults["crux"]

    date_matches = list(dict.fromkeys(re.findall(
        r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b",
        source, re.IGNORECASE,
    )))
    for item in date_matches[:3]:
        important_dates.append({"label": defaults["important_date_label"], "value": item, "note": defaults["important_date_note"]})
    important_dates = _enrich_important_dates(important_dates, source, defaults)

    amount_match = re.search(r"(?:Rs\.?|INR|\$|EUR|USD)\s?[\d,]+(?:\.\d{1,2})?", source, re.IGNORECASE)
    if amount_match:
        important_points.append({"label": defaults["amount_label"], "value": amount_match.group(0), "note": defaults["amount_note"]})

    id_match = re.search(r"\b[A-Z]{2,}[0-9]{2,}\b", source)
    if id_match:
        important_points.append({"label": defaults["reference_id_label"], "value": id_match.group(0), "note": defaults["reference_id_note"]})

    lowered = source.lower()
    medical_keywords = ["diagnosis", "symptom", "treatment", "tablet", "dosage", "bp",
                        "blood pressure", "heart rate", "lab result", "lab values",
                        "medicine", "mri", "x-ray", "ultrasound", "patient", "prescribed"]
    for keyword in medical_keywords:
        if re.search(rf"\b{re.escape(keyword)}\b", lowered):
            important_points.append({
                "label": defaults["medical_detail_label"],
                "value": keyword.title(),
                "note": defaults["medical_detail_note"].format(keyword=keyword),
            })
            break

    diagnostic_keywords = ["hemoglobin", "wbc", "rbc", "platelet", "hba1c", "glucose",
                           "creatinine", "bilirubin", "cholesterol", "triglycerides",
                           "thyroid", "tsh", "x-ray", "mri", "ultrasound", "ecg"]
    for diag in [k for k in diagnostic_keywords if re.search(rf"\b{re.escape(k)}\b", lowered)][:2]:
        important_points.append({
            "label": defaults["diagnostic_label"],
            "value": diag.upper() if len(diag) <= 4 else diag.title(),
            "note": defaults["diagnostic_note"].format(value=diag),
        })

    symptom_keywords = ["fever", "cough", "pain", "vomiting", "fatigue",
                        "weakness", "headache", "swelling", "infection", "inflammation"]
    for symptom in [k for k in symptom_keywords if re.search(rf"\b{re.escape(k)}\b", lowered)][:2]:
        important_points.append({"label": defaults["symptom_label"], "value": symptom.title(), "note": defaults["symptom_note"].format(value=symptom)})

    if any(k in lowered for k in ["diagnosis", "patient", "lab", "hemoglobin", "wbc", "rbc", "blood"]):
        inferred_doc_type = "medical"
    elif any(k in lowered for k in ["loan", "emi", "interest", "statement", "bank", "account"]):
        inferred_doc_type = "bank"
    elif any(k in lowered for k in ["scheme", "eligibility", "benefit", "application", "deadline", "notice", "government"]):
        inferred_doc_type = "government"
    else:
        inferred_doc_type = "unknown"

    inferred_summary = _human_summary(inferred_doc_type, source, language)
    crux = inferred_crux
    medical_conclusion = ""
    lang_key = str(language or "English").strip().lower()

    if inferred_crux == defaults["crux"] and important_dates:
        crux = (f"इस दस्तावेज़ में कम से कम {len(important_dates)} महत्वपूर्ण तिथि(यां) हैं।" if lang_key == "hindi"
                else f"ఈ పత్రంలో కనీసం {len(important_dates)} ముఖ్యమైన తేదీలు ఉన్నాయి." if lang_key == "telugu"
                else f"This document contains at least {len(important_dates)} important date(s) that may be central to the content.")
    elif inferred_crux == defaults["crux"] and important_points and any(item.get("label") == defaults["medical_detail_label"] for item in important_points):
        if lang_key == "hindi":
            crux = "इस दस्तावेज़ में मेडिकल जानकारी है, जो समीक्षा के लिए महत्वपूर्ण हो सकती है।"
            medical_conclusion = "मेडिकल निष्कर्ष: दस्तावेज़ में संभावित चिकित्सकीय रूप से महत्वपूर्ण जानकारी मिली है।"
        elif lang_key == "telugu":
            crux = "ఈ పత్రంలో వైద్య సమాచారం ఉంది, ఇది సమీక్షకు ముఖ్యమైనది కావచ్చు."
            medical_conclusion = "వైద్య నిర్ధారణ: పత్రంలో వైద్యపరంగా ముఖ్యమైన సమాచారం ఉండే అవకాశం ఉంది."
        else:
            crux = "This document appears to contain medical information that may be important for review."
            medical_conclusion = "Medical conclusion: the document appears to contain potentially important clinical information."
    elif inferred_crux == defaults["crux"] and important_points:
        crux = ("इस दस्तावेज़ में प्रमुख संदर्भ या वित्तीय विवरण हैं, जो महत्वपूर्ण हो सकते हैं।" if lang_key == "hindi"
                else "ఈ పత్రంలో ముఖ్యమైన రిఫరెన్స్ లేదా ఆర్థిక వివరాలు ఉన్నాయి, ఇవి ముఖ్యమైనవి కావచ్చు." if lang_key == "telugu"
                else "This document contains key reference or financial details that may be important.")

    if important_dates:
        highlights.extend({"name": i["label"], "value": i["value"], "status": "deadline", "note": i.get("note", "")} for i in important_dates)
    if important_points:
        highlights.extend({"name": i["label"], "value": i["value"], "status": "important", "note": i.get("note", "")} for i in important_points)

    if not highlights:
        highlights.append({"name": defaults["text_extracted_name"], "value": f"{len(source.split())} words", "status": "normal", "note": defaults["text_extracted_note"]})

    important_points = _prioritize_points(important_points, defaults, max_items=5)
    for date_item in important_dates[:2]:
        if len(important_points) >= 5:
            break
        important_points.append({"label": defaults["deadline_label"], "value": _trim_text(date_item.get("value", "")), "note": _trim_text(date_item.get("note", "")) or defaults["deadline_note"]})
    important_points = _prioritize_points(important_points, defaults, max_items=5)

    return {
        "doc_type": "medical" if medical_conclusion else ("government" if important_dates else inferred_doc_type),
        "doc_title": defaults["doc_title"],
        "crux": crux,
        "summary": inferred_summary,
        "medical_conclusion": medical_conclusion,
        "important_dates": important_dates[:3],
        "important_points": important_points[:5],
        "highlights": highlights[:5],
    }
