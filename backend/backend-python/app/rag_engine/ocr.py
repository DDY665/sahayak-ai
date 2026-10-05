from __future__ import annotations

import base64
import io
import logging
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_core.documents import Document

load_dotenv()
logger = logging.getLogger(__name__)


def _get_groq_vision_client():
    from groq import Groq

    api_key = (
        os.getenv("GROQ_CHAT_API_KEY", "").strip()
        or os.getenv("GROQ_API_KEY", "").strip()
        or os.getenv("GROQ_SUMMARY_API_KEY", "").strip()
    )
    if not api_key:
        logger.warning("[OCR] No Groq API key found in environment.")
        return None
    return Groq(api_key=api_key)


def ocr_image_bytes(img_bytes: bytes, filename: str = "", max_dim: int = 1600) -> str:
    """Run Vision OCR on raw image bytes using Groq vision model."""
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(img_bytes))
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        w, h = img.size
        if max(w, h) > max_dim:
            scale = max_dim / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        client = _get_groq_vision_client()
        if client is None:
            return ""

        model = os.getenv("VISION_MODEL", "qwen/qwen3.8-27b")
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "You are an OCR extraction engine. Extract all readable text, titles, "
                                "numbers, tables, names, ID numbers, and labels from this document image accurately. "
                                "Return only the extracted text. Do not include conversational remarks or explanations."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                        },
                    ],
                }
            ],
            temperature=0,
        )
        extracted = resp.choices[0].message.content or ""
        logger.info(f"[OCR] Extracted {len(extracted)} chars from image in {filename}")
        return extracted.strip()
    except Exception as exc:
        logger.warning(f"[OCR] Failed to extract text from image ({filename}): {exc}")
        return ""


def extract_ocr_from_pdf(file_path: str) -> List[Document]:
    """Inspect PDF for images and run Vision OCR on scanned/image pages."""
    try:
        import pypdf

        reader = pypdf.PdfReader(file_path)
        docs: List[Document] = []
        source_name = Path(file_path).name

        for page_idx, page in enumerate(reader.pages):
            page_text = (page.extract_text() or "").strip()
            ocr_text_parts = []

            if len(page_text) < 50 and len(page.images) > 0:
                logger.info(
                    f"[OCR] PDF {source_name} page {page_idx+1} has {len(page.images)} image(s) and minimal text. Running OCR..."
                )
                for img_idx, img in enumerate(page.images):
                    if len(img.data) >= 2048:
                        txt = ocr_image_bytes(
                            img.data,
                            filename=f"{source_name}_p{page_idx+1}_img{img_idx+1}",
                        )
                        if txt:
                            ocr_text_parts.append(txt)

            combined_page_text = page_text
            if ocr_text_parts:
                combined_page_text = (
                    f"{page_text}\n\n" + "\n\n".join(ocr_text_parts)
                    if page_text
                    else "\n\n".join(ocr_text_parts)
                )

            if combined_page_text.strip():
                docs.append(
                    Document(
                        page_content=combined_page_text.strip(),
                        metadata={"source": source_name, "page": page_idx + 1},
                    )
                )

        return docs
    except Exception as exc:
        logger.warning(f"[OCR] PDF OCR fallback failed for {file_path}: {exc}")
        return []


def extract_ocr_from_image(file_path: str) -> List[Document]:
    """Run Vision OCR on standalone image files (png, jpg, jpeg, webp)."""
    try:
        data = Path(file_path).read_bytes()
        source_name = Path(file_path).name
        text = ocr_image_bytes(data, filename=source_name)
        if not text:
            return []
        return [Document(page_content=text, metadata={"source": source_name, "page": 1})]
    except Exception as exc:
        logger.warning(f"[OCR] Standalone image OCR failed for {file_path}: {exc}")
        return []
