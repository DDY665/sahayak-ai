from __future__ import annotations

from datetime import datetime, timezone
import json
import logging


def configure_logging() -> logging.Logger:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    return logging.getLogger("sahayakai-python")


def emit_log(event: str, level: str = "info", **fields) -> str:
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level.upper(),
        "event": event,
        **fields,
    }
    return json.dumps(payload, ensure_ascii=False)
