from __future__ import annotations

import re

from .context_summary import _build_context_summary
from .text_utils import _extract_subject_name, _summary_is_generic, _summary_looks_noisy
from .item_utils import _trim_text


def _human_summary(doc_type: str, preview: str, language: str) -> str:
    lang_key = str(language or "English").strip().lower()
    subject = _extract_subject_name(preview)

    if doc_type == "medical":
        if lang_key == "hindi":
            base = f"यह {'श्री/सुश्री ' + subject + ' की ' if subject else 'एक '}मेडिकल रिपोर्ट है।"
            return f"{base} इसमें जाँच परिणाम और महत्वपूर्ण चिकित्सीय संकेत दर्ज हैं। कोई भी असामान्य परिणाम हो तो डॉक्टर से तुरंत परामर्श लें।"
        if lang_key == "telugu":
            base = f"ఇది {'శ్రీ/శ్రీమతి ' + subject + ' యొక్క ' if subject else 'ఒక '}వైద్య నివేదిక."
            return f"{base} ఇందులో పరీక్ష ఫలితాలు మరియు ముఖ్యమైన వైద్య సంకేతాలు ఉన్నాయి. ఏదైనా అసాధారణత ఉంటే వైద్యుని సంప్రదించండి."
        base = f"This is a medical report{' for ' + subject if subject else ''}."
        return f"{base} It contains test results and clinically important findings. Consult your doctor if any value appears abnormal."

    if doc_type == "bank":
        if lang_key == "hindi":
            return "यह एक बैंक या वित्तीय दस्तावेज़ है। इसमें राशि, देय तिथि और ब्याज से जुड़े महत्वपूर्ण बिंदु हैं। समय पर भुगतान करें और किसी भी विसंगति की स्थिति में बैंक से संपर्क करें।"
        if lang_key == "telugu":
            return "ఇది ఒక బ్యాంకు లేదా ఆర్థిక పత్రం. ఇందులో చెల్లింపు తేదీలు, మొత్తాలు మరియు వడ్డీకి సంబంధించిన ముఖ్య వివరాలు ఉన్నాయి. సకాలంలో చెల్లించి జరిమానాలు నివారించండి."
        return "This is a bank or financial document. It includes important details such as amounts, due dates, and interest. Pay on time and contact your bank if anything looks incorrect."

    if doc_type == "government":
        if lang_key == "hindi":
            return "यह एक सरकारी या योजना दस्तावेज़ है। इसमें पात्रता की शर्तें, आवश्यक दस्तावेज़ और लाभ की जानकारी दी गई है। समय-सीमा से पहले आवेदन करना सुनिश्चित करें।"
        if lang_key == "telugu":
            return "ఇది ఒక ప్రభుత్వ లేదా పథక పత్రం. ఇందులో అర్హత, అవసరమైన పత్రాలు మరియు ప్రయోజనాల వివరాలు ఉన్నాయి. గడువు తేదీకి ముందే దరఖాస్తు చేయండి."
        return "This is a government or scheme document. It covers eligibility, required documents, benefits, and important deadlines. Ensure you apply before the deadline to receive the benefits."

    if lang_key == "hindi":
        return "यह दस्तावेज़ महत्वपूर्ण जानकारी रखता है। इसे ध्यान से पढ़कर आवश्यक कदम उठाएं और किसी भी समय-सीमा का विशेष ध्यान रखें।"
    if lang_key == "telugu":
        return "ఈ పత్రంలో ముఖ్యమైన సమాచారం ఉంది. దీన్ని జాగ్రత్తగా చదివి తగిన చర్యలు తీసుకోండి మరియు ఏదైనా గడువు తేదీని మిస్ చేయకండి."
    return "This document contains important information. Read it carefully, take the necessary steps, and make sure not to miss any deadlines or key actions mentioned."


def _finalize_summary_with_context(
    summary: str,
    doc_type: str,
    preview: str,
    language: str,
    important_dates: list[dict],
    important_points: list[dict],
) -> str:
    s = _trim_text(summary)
    if not s or _summary_looks_noisy(s) or _summary_is_generic(s):
        s = _build_context_summary(doc_type, preview, important_dates, important_points, language)

    s = re.sub(r"\s+", " ", s).strip()
    parts = [p.strip() for p in re.split(r"(?<=[.!?।])\s+", s) if p.strip()]
    if not parts:
        parts = [s]
    s = " ".join(parts[:6]).strip()

    words = s.split()
    if len(words) > 95:
        s = " ".join(words[:95]).rstrip(" ,;:-") + "..."

    if _summary_looks_noisy(s) or _summary_is_generic(s):
        s = _build_context_summary(doc_type, preview, important_dates, important_points, language)

    return s
