from __future__ import annotations

from .item_utils import _trim_text
from .text_utils import _extract_subject_name


def _build_context_summary(
    doc_type: str,
    preview: str,
    important_dates: list[dict],
    important_points: list[dict],
    language: str,
) -> str:
    lang_key = str(language or "English").strip().lower()
    subject = _extract_subject_name(preview)

    def first_value(items: list[dict]) -> str:
        for item in items:
            value = _trim_text(item.get("value", ""))
            if value:
                return value
        return ""

    top_date = first_value(important_dates)
    top_point = first_value(important_points)

    if lang_key == "hindi":
        if doc_type == "medical":
            lines = [
                "यह एक मेडिकल/लैब रिपोर्ट है।",
                f"यह मुख्य रूप से {subject} से संबंधित है।" if subject else "यह किसी मरीज या मेडिकल केस से संबंधित लगती है।",
                "इसमें जांच परिणाम, चिकित्सीय संकेत और क्लिनिकल विवरण दिए गए हैं।",
                f"महत्वपूर्ण बिंदु: {top_point}." if top_point else "महत्वपूर्ण चिकित्सीय बिंदुओं पर ध्यान देना चाहिए।",
                f"ध्यान देने योग्य तिथि: {top_date}." if top_date else "ज़रूरत हो तो मैं इसे टेस्ट-वाइज आसान भाषा में समझा सकता हूँ।",
            ]
            return " ".join(line for line in lines if line)
        if doc_type == "bank":
            lines = [
                "यह एक बैंक/वित्तीय दस्तावेज़ है।",
                "यह भुगतान, देय तिथि, ब्याज, राशि या खाते से जुड़ी जानकारी समझाता है।",
                f"मुख्य बिंदु: {top_point}." if top_point else "मुख्य वित्तीय बिंदुओं पर ध्यान देना चाहिए।",
                f"महत्वपूर्ण तिथि: {top_date}." if top_date else "ज़रूरत हो तो मैं इसे कार्रवाई योग्य बिंदुओं में बदल सकता हूँ।",
            ]
            return " ".join(line for line in lines if line)
        if doc_type == "government":
            lines = [
                "यह एक सरकारी/योजना दस्तावेज़ है।",
                "यह पात्रता, लाभ, आवश्यक दस्तावेज़ और समय-सीमाओं की जानकारी देता है।",
                f"मुख्य बिंदु: {top_point}." if top_point else "मुख्य योजना/प्रक्रिया बिंदुओं पर ध्यान देना चाहिए।",
                f"महत्वपूर्ण तिथि: {top_date}." if top_date else "ज़रूरत हो तो मैं इसे सरल भाषा में समझा सकता हूँ।",
            ]
            return " ".join(line for line in lines if line)
        lines = [
            "यह दस्तावेज़ महत्वपूर्ण जानकारी समझाने के लिए है।",
            "यह बताता है कि दस्तावेज़ किस बारे में है और किन बातों पर ध्यान देना चाहिए।",
            f"मुख्य बिंदु: {top_point}." if top_point else "इसमें कुछ प्रमुख बातें शामिल हैं।",
            f"महत्वपूर्ण तिथि: {top_date}." if top_date else "ज़रूरत हो तो मैं इसे और स्पष्ट हिस्सों में समझा सकता हूँ।",
        ]
        return " ".join(line for line in lines if line)

    if lang_key == "telugu":
        if doc_type == "medical":
            lines = [
                "ఇది ఒక వైద్య/ల్యాబ్ నివేదిక.",
                f"ఇది ప్రధానంగా {subject} గురించి ఉంది." if subject else "ఇది ఒక రోగి లేదా వైద్య కేసుకు సంబంధించినదిగా కనిపిస్తోంది.",
                "ఇందులో పరీక్ష ఫలితాలు, వైద్య సంకేతాలు మరియు క్లినికల్ వివరాలు ఉన్నాయి.",
                f"ముఖ్య అంశం: {top_point}." if top_point else "ముఖ్యమైన వైద్య అంశాలపై దృష్టి పెట్టాలి.",
                f"గమనించాల్సిన తేదీ: {top_date}." if top_date else "అవసరమైతే దీన్ని పరీక్షల వారీగా సులభంగా వివరించగలను.",
            ]
            return " ".join(line for line in lines if line)
        if doc_type == "bank":
            lines = [
                "ఇది ఒక బ్యాంకు/ఆర్థిక పత్రం.",
                "ఇది చెల్లింపులు, గడువు, వడ్డీ, మొత్తం లేదా ఖాతా వివరాలను చెబుతుంది.",
                f"ముఖ్య అంశం: {top_point}." if top_point else "ముఖ్యమైన ఆర్థిక విషయాలపై దృష్టి పెట్టాలి.",
                f"ముఖ్య తేదీ: {top_date}." if top_date else "అవసరమైతే దీన్ని చేయాల్సిన చర్యలుగా మార్చగలను.",
            ]
            return " ".join(line for line in lines if line)
        if doc_type == "government":
            lines = [
                "ఇది ఒక ప్రభుత్వ/పథక పత్రం.",
                "ఇది అర్హత, ప్రయోజనాలు, అవసరమైన పత్రాలు మరియు గడువులను వివరిస్తుంది.",
                f"ముఖ్య అంశం: {top_point}." if top_point else "పథకం/ప్రక్రియకు సంబంధించిన ముఖ్య అంశాలపై దృష్టి పెట్టాలి.",
                f"ముఖ్య తేదీ: {top_date}." if top_date else "అవసరమైతే దీన్ని సులభంగా వివరించగలను.",
            ]
            return " ".join(line for line in lines if line)
        lines = [
            "ఈ పత్రం ముఖ్యమైన సమాచారాన్ని అర్థం చేసుకోవడానికి ఉంది.",
            "ఇది పత్రం ఏ విషయం గురించి ఉందో మరియు ఏ విషయాలపై దృష్టి పెట్టాలో చెబుతుంది.",
            f"ముఖ్య అంశం: {top_point}." if top_point else "ఇందులో కొన్ని ముఖ్యమైన విషయాలు ఉన్నాయి.",
            f"ముఖ్య తేదీ: {top_date}." if top_date else "అవసరమైతే దీనిని మరింత స్పష్టమైన భాగాలుగా విడగొట్టగలను.",
        ]
        return " ".join(line for line in lines if line)

    # English (default)
    if doc_type == "medical":
        lines = [
            "This is a medical/lab report.",
            f"It is mainly about {subject}." if subject else "It appears to concern a patient or a medical case.",
            "It explains test results, clinical observations, and health-related details.",
            f"Key point: {top_point}." if top_point else "The main focus is on the important medical findings.",
            f"Important date: {top_date}." if top_date else "I can break it down test-by-test in simple language if needed.",
        ]
        return " ".join(line for line in lines if line)
    if doc_type == "bank":
        lines = [
            "This is a bank/financial document.",
            "It explains payments, due dates, interest, amounts, or account-related details.",
            f"Key point: {top_point}." if top_point else "The key financial points are worth paying attention to.",
            f"Important date: {top_date}." if top_date else "I can turn it into clear action items if needed.",
        ]
        return " ".join(line for line in lines if line)
    if doc_type == "government":
        lines = [
            "This is a government/scheme document.",
            "It explains eligibility, benefits, required documents, and deadlines.",
            f"Key point: {top_point}." if top_point else "The main scheme or process details matter most.",
            f"Important date: {top_date}." if top_date else "I can simplify it into plain action steps if needed.",
        ]
        return " ".join(line for line in lines if line)

    lines = [
        "This document contains important information.",
        "It explains what the file is about and what the reader should focus on.",
        f"Key point: {top_point}." if top_point else "It includes a few useful details worth reviewing.",
        f"Important date: {top_date}." if top_date else "I can explain it further in simpler terms if needed.",
    ]
    return " ".join(line for line in lines if line)
