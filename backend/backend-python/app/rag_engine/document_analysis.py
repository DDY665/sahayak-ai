from __future__ import annotations

import json
import logging
import re

from app.analysis import (
    build_analysis_prompt,
    fallback_analysis,
    normalize_analysis,
    parse_analysis_json,
)

logger = logging.getLogger(__name__)


class RAGDocumentAnalysisMixin:
    def analyze_file(self, file_path: str, language: str = "English") -> dict:
        """Generate structured analysis for UI display."""
        try:
            docs = self._load_documents(file_path)
            text = "\n\n".join(doc.page_content for doc in docs)
            # Keep prompt size stable for consistent JSON responses on long PDFs.
            preview = " ".join(text.split()[:1200])
            if not preview.strip():
                raise ValueError("Document is empty")

            prompt = build_analysis_prompt(language=language, preview=preview)
            response = self.summary_llm.invoke(prompt)
            try:
                parsed = parse_analysis_json(getattr(response, "content", str(response)))
            except Exception:
                # Retry once with full schema instructions to reduce fallback outputs.
                retry_prompt = (
                    "IMPORTANT: Return ONLY valid JSON. No markdown, no prose.\n"
                    + build_analysis_prompt(language=language, preview=preview)
                )
                retry_response = self.summary_llm.invoke(retry_prompt)
                parsed = parse_analysis_json(getattr(retry_response, "content", str(retry_response)))

            normalized = normalize_analysis(parsed, preview=preview, language=language)
            return self._localize_analysis_if_needed(normalized, language)
        except Exception as exc:
            logger.warning("Structured analysis failed; using fallback: %s", exc)
            return fallback_analysis(preview if "preview" in locals() else "", language=language)

    def _localize_analysis_if_needed(self, analysis: dict, language: str) -> dict:
        lang = str(language or "English").strip().lower()
        if lang not in {"hindi", "telugu"}:
            return analysis
        if not self._analysis_looks_english(analysis, lang):
            return analysis

        language_name = "Hindi" if lang == "hindi" else "Telugu"
        try:
            payload = json.dumps(analysis, ensure_ascii=False)
            prompt = f"""
Translate the following JSON document analysis to {language_name}.

Rules:
- Return ONLY valid JSON.
- Keep the same JSON keys and structure exactly.
- Keep numbers, dates, and status values unchanged.
- Translate all user-facing text fields like doc_title, crux, summary, labels, names, values, and notes.
- Do not add or remove items.

JSON:
{payload}
""".strip()
            response = self.summary_llm.invoke(prompt)
            parsed = self._parse_analysis_json_lenient(getattr(response, "content", str(response)))
            return normalize_analysis(parsed, preview="", language=language)
        except Exception as exc:
            logger.warning("Analysis localization failed on first attempt: %s", exc)

        try:
            retry_prompt = (
                f"Convert this JSON to {language_name}. Return ONLY valid JSON, no markdown, no explanation.\n"
                "Keep keys/structure/status unchanged. Keep numbers and dates unchanged.\n"
                f"JSON:\n{json.dumps(analysis, ensure_ascii=False)}"
            )
            retry_response = self.summary_llm.invoke(retry_prompt)
            parsed_retry = self._parse_analysis_json_lenient(getattr(retry_response, "content", str(retry_response)))
            return normalize_analysis(parsed_retry, preview="", language=language)
        except Exception as retry_exc:
            logger.warning("Analysis localization retry failed: %s", retry_exc)
            return analysis

    def _parse_analysis_json_lenient(self, raw_text: str) -> dict:
        try:
            return parse_analysis_json(raw_text)
        except Exception:
            text = str(raw_text or "")
            match = re.search(r"\{[\s\S]*\}", text)
            if not match:
                raise
            candidate = match.group(0)
            parsed = json.loads(candidate)
            if not isinstance(parsed, dict):
                raise ValueError("Localized analysis payload is not a JSON object")
            return parsed

    def _analysis_looks_english(self, analysis: dict, language_key: str) -> bool:
        target_script = r"[\u0900-\u097F]" if language_key == "hindi" else r"[\u0C00-\u0C7F]"
        samples: list[str] = [
            str(analysis.get("doc_title", "")),
            str(analysis.get("crux", "")),
            str(analysis.get("summary", "")),
        ]
        for section_name in ("important_dates", "important_points", "medical_conclusion", "medical_details", "important_details", "highlights"):
            section = analysis.get(section_name, [])
            if not isinstance(section, list):
                if section_name == "medical_conclusion" and isinstance(section, str):
                    samples.append(section)
                continue
            for item in section[:5]:
                if not isinstance(item, dict):
                    continue
                for key in ("label", "name", "value", "note"):
                    if key in item:
                        samples.append(str(item.get(key, "")))
        combined = " ".join(s for s in samples if s).strip()
        if not combined:
            return False
        if re.search(target_script, combined) is not None:
            return False
        return len(re.findall(r"[A-Za-z]", combined)) >= 20
