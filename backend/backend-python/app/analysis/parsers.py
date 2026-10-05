from __future__ import annotations

import ast
import json
import re


def parse_analysis_json(raw_text: str) -> dict:
    raw = str(raw_text or "").strip()
    # Fast path: exact JSON payload.
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    # Common model pattern: fenced code block with optional `json` tag.
    if raw.startswith("```"):
        parts = raw.split("```")
        if len(parts) > 1:
            raw = parts[1]
            if raw.lower().startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass

    # Lenient path: extract first JSON object from mixed text.
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = raw[start : end + 1]
        # Remove trailing commas that sometimes appear before closing braces/brackets.
        candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
        try:
            parsed = json.loads(candidate)
        except Exception:
            parsed = ast.literal_eval(candidate)
    else:
        raise ValueError("Invalid analysis payload")

    if not isinstance(parsed, dict):
        raise ValueError("Invalid analysis payload")
    return parsed
