from __future__ import annotations


class RAGClarificationMixin:
    def _is_ambiguous_question(self, question: str) -> bool:
        text = str(question or "").strip().lower()
        if not text:
            return True
        vague_starters = {
            "tell me", "explain", "what about", "what is this", "what's this",
            "about this", "summarize", "summary", "details", "more", "that", "it", "this",
        }
        direct_keywords = {
            "date", "deadline", "eligibility", "amount", "emi", "interest",
            "penalty", "diagnosis", "test", "result", "value", "range", "section", "page",
        }
        words = text.split()
        if len(words) == 1 and text in {"help", "summary", "summarize", "overview", "details", "info"}:
            return True
        return False

    def _clarification_locale(self, language: str) -> dict[str, str]:
        key = str(language or "English").lower()
        if key == "hindi":
            return {
                "prompt": "आपको सबसे उपयोगी उत्तर देने के लिए एक छोटा स्पष्टीकरण चाहिए: आप क्या चाहते हैं?",
                "options": (
                    "1) त्वरित सारांश, 2) महत्वपूर्ण तिथियां/समय-सीमाएं, 3) पैसे/वित्तीय प्रभाव, "
                    "4) पात्रता/नियम, 5) चिकित्सीय विवरण (जांच, रेंज, असामान्यताएं)."
                ),
                "fallback": "अगर आप कुछ नहीं बताते, तो मैं 5-बिंदु सारांश दूँगा।",
                "default_question": (
                    "इस दस्तावेज़ का 5-बिंदु सारांश दीजिए, और महत्वपूर्ण तिथियाँ/समय-सीमाएँ, "
                    "महत्वपूर्ण राशियाँ या संख्यात्मक मान, और सबसे महत्वपूर्ण कार्रवाई के बिंदु भी शामिल कीजिए।"
                ),
            }
        if key == "telugu":
            return {
                "prompt": "మీకు సరైన సహాయం చేయడానికి ఒక చిన్న స్పష్టీకరణ కావాలి: మీకు ఏమి కావాలి?",
                "options": (
                    "1) త్వరిత సారాంశం, 2) ముఖ్య తేదీలు/గడువులు, 3) డబ్బు/ఆర్థిక ప్రభావం, "
                    "4) అర్హత/నియమాలు, 5) వైద్య వివరాలు (పరీక్షలు, పరిధులు, అసాధారణతలు)."
                ),
                "fallback": "మీరు ఏదీ పేర్కొనకపోతే, నేను 5-బిందువుల సారాంశం ఇస్తాను.",
                "default_question": (
                    "ఈ పత్రానికి 5-బిందువుల సారాంశం ఇవ్వండి, అలాగే ముఖ్య తేదీలు/గడువులు, "
                    "ప్రధాన మొత్తాలు లేదా సంఖ్యాత్మక విలువలు, మరియు అత్యంత ముఖ్యమైన చర్యా అంశాలను కూడా చేర్చండి."
                ),
            }
        return {
            "prompt": "To give you the most accurate answer, what do you want most from this document right now:",
            "options": (
                "1) quick summary, 2) important dates/deadlines, 3) money/financial impact, "
                "4) eligibility/rules, 5) medical details (tests, ranges, abnormalities)."
            ),
            "fallback": "If you do not specify, I will give a 5-point summary.",
            "default_question": (
                "Give a concise 5-point summary of this document, and include key dates/deadlines, "
                "critical amounts or numeric values, and the most important action items."
            ),
        }

    def _build_clarifying_question(self, language: str = "English") -> str:
        locale = self._clarification_locale(language)
        return f"{locale['prompt']} {locale['options']} {locale['fallback']}"

    def _has_recent_clarification_prompt(self, history: list[dict] | None = None) -> bool:
        if not history:
            return False
        markers = (
            "to give you the most accurate answer", "5-point summary",
            "aapko sabse useful answer", "meeku accurate ga help",
        )
        for item in reversed(history[-6:]):
            role = str(item.get("role", "")).lower()
            if role != "assistant":
                continue
            if any(marker in str(item.get("content", "")).lower() for marker in markers):
                return True
        return False

    def _default_scope_question(self, language: str = "English") -> str:
        return self._clarification_locale(language)["default_question"]

    def _build_chat_prompt_inputs(
        self, question: str, context: str, language: str, history: list[dict] | None = None,
    ) -> dict:
        history_context = "\n".join([
            f"{str(item.get('role', 'user')).upper()}: {str(item.get('content', ''))}"
            for item in (history or [])[-6:]
        ])
        return {
            "question": question,
            "context": context,
            "language": language,
            "history_context": history_context or "None",
        }
