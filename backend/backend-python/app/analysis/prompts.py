from __future__ import annotations


def build_analysis_prompt(language: str, preview: str) -> str:
    return f"""You are a document analysis expert.
Analyze the document and return ONLY valid JSON.

First classify the document:
- medical: lab report, prescription, diagnosis, discharge summary
- bank: statement, loan, EMI, interest, credit card, penalty
- government: scheme, eligibility, notice, deadline, benefit
- unknown: none of the above

Then extract high-impact details.
For medical docs, prioritize tests, values, units, ranges, abnormal markers, and follow-up implications.
For bank docs, prioritize interest rates, EMI, penalties, outstanding dues, and payable dates.
For government docs, prioritize eligibility, required documents, benefits, and deadlines.

Only include sections that are relevant to the document.

SUMMARY RULES (strictly follow these):
- Write a clean 4-5 sentence paragraph in {language}.
- Explain what this document is, who it concerns, and what the reader should pay attention to.
- Do NOT copy raw values, table rows, numeric data, or lab result lines into the summary.
- Write in plain human language as if explaining to a non-expert who has never seen this document.
- End with exactly 1 sentence highlighting the single most important takeaway or action item.
- Never start with phrases like "This document contains" or "Document uploaded".

IMPORTANT POINTS RULES:
- Extract 3-5 genuinely important points from the document (not generic labels).
- Each point must have a clear label, a specific value, and a plain-language note explaining why it matters.
- Do not repeat information already in the summary.

OTHER RULES:
- Include important dates only if the document has dates or deadlines that matter.
- Include medical conclusion only for medical documents.
- Always provide a crux (1-2 sentences, the core meaning).

Return ONLY valid JSON with this schema:
{{
  "doc_type": "medical" | "bank" | "government" | "unknown",
  "doc_title": "short title in {language}",
  "crux": "1-2 sentence core meaning of the document in {language}",
    "summary": "4-5 sentence plain-language paragraph in {language} — NO raw values or table data",
    "medical_conclusion": "short conclusion in {language} or empty string",
  "important_dates": [
    {{
            "label": "date label in {language}",
      "value": "date value",
      "note": "why it matters in {language}"
    }}
  ],
    "important_points": [
    {{
            "label": "important point label in {language}",
            "value": "value in {language}",
      "note": "why it matters in {language}"
    }}
  ],
  "highlights": [
    {{
            "name": "field name in {language}",
            "value": "value in {language}",
      "reference_range": "normal range if present (medical only)",
      "status": "normal|high|low|warning|attention|important|deadline",
      "note": "plain-language note in {language}"
    }}
  ]
}}

Rules:
- Write ALL user-facing text in {language}.
- Keep numeric/date values unchanged where possible.
- Extract up to 5 high-signal highlights only.
- Keep important_points concise and relevant (max 5), each with a specific value — not vague labels.
- Summary MUST be a readable paragraph (4-5 sentences), never a list or raw data dump.
- If a date appears critical, include it under important_dates.
- If the document is not medical, medical_conclusion must be an empty string.
- If information is missing, use empty arrays but still provide crux and summary.

Document text:
{preview}
"""
