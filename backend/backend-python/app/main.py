from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import json
import os
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from bson import ObjectId

from app.core.database import connect_db, close_db, get_db
from app.core.auth import get_optional_user
from app.core.logging_utils import configure_logging, emit_log
from app.core.middleware import create_request_id_middleware
from app.models import now_utc
from app.rag_engine import RAGEngine
from app.schemas import AskRequest, AskResponse, DocumentInfo
from app.routers.auth import router as auth_router
from app.routers.conversations import router as conversations_router
from app.routers.history import router as history_router

load_dotenv()
_env_candidates = [
    Path.cwd() / ".env",
    Path(__file__).resolve().parent.parent / ".env",
    Path(__file__).resolve().parent.parent.parent / ".env",
]
for _env_path in _env_candidates:
    if _env_path.exists():
        load_dotenv(_env_path)

logger = configure_logging()

base_upload_dir = Path(os.getenv("UPLOAD_DIR", "./uploads"))
base_upload_dir.mkdir(parents=True, exist_ok=True)

rag_engine = RAGEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing SahayakAI backend...")
    try:
        await connect_db()
    except Exception as exc:
        logger.warning(f"MongoDB connection failed on startup: {exc}. Continuing...")
    yield
    logger.info("Shutting down SahayakAI backend...")
    await close_db()


app = FastAPI(
    title="SahayakAI API Service",
    version="2.0.0",
    description="Unified SahayakAI FastAPI Backend (Auth + Database + RAG Engine)",
    lifespan=lifespan,
)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"^https?:\/\/.*$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(create_request_id_middleware(logger))

app.include_router(auth_router)
app.include_router(conversations_router)
app.include_router(history_router)


def _resolve_upload_dir(user_id: str | None, chat_id: str | None) -> Path:
    uid = user_id.strip() if user_id and user_id.strip() else "anonymous"
    cid = chat_id.strip() if chat_id and chat_id.strip() else "default"
    upload_path = base_upload_dir / uid / cid
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "SahayakAI FastAPI 2.0",
        "node": "ok",
        "python": "ok",
    }


@app.post("/api/upload")
@app.post("/ingest")
async def handle_upload(
    request: Request,
    file: UploadFile = File(...),
    language: str = Form("English"),
    conversationId: Optional[str] = Form(None),
    chat_id: Optional[str] = Form(None),
    userId: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    current_user: Optional[dict] = Depends(get_optional_user),
) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name")

    effective_user_id = (
        (current_user["id"] if current_user else None)
        or userId
        or user_id
        or "anonymous"
    )
    raw_conv_id = conversationId or chat_id
    is_new_conv = not bool(raw_conv_id and str(raw_conv_id).strip())
    if is_new_conv:
        effective_conv_id = str(ObjectId()) if effective_user_id != "anonymous" else "default"
    else:
        effective_conv_id = str(raw_conv_id).strip()

    upload_dir = _resolve_upload_dir(effective_user_id, effective_conv_id)
    destination = upload_dir / file.filename

    content = await file.read()
    logger.info(
        f"[UPLOAD-START] filename={file.filename}, size={len(content)} bytes, "
        f"userId={effective_user_id}, convId={effective_conv_id}"
    )
    destination.write_bytes(content)

    session_user = effective_user_id if effective_user_id else "anonymous"
    session_chat = effective_conv_id

    try:
        chunk_count = rag_engine.ingest_file_for_session(
            str(destination),
            user_id=session_user,
            chat_id=session_chat,
        )
        logger.info(f"[UPLOAD-INDEXED] filename={file.filename}, chunks={chunk_count}")
    except Exception as exc:
        logger.error(f"[UPLOAD-INDEX-FAILED] filename={file.filename}, error={exc}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc

    analysis = {
        "doc_type": "unknown",
        "doc_title": file.filename,
        "summary": "Document uploaded successfully. You can now ask questions about it.",
        "highlights": [],
    }

    try:
        analysis = await asyncio.wait_for(
            asyncio.to_thread(rag_engine.analyze_file, str(destination), language),
            timeout=float(os.getenv("ANALYSIS_TIMEOUT_SECONDS", "45")),
        )
    except Exception as exc:
        logger.warning(
            emit_log(
                "analysis.fallback",
                level="warning",
                filename=file.filename,
                request_id=getattr(request.state, "request_id", "unknown"),
                reason=str(exc),
            )
        )

    db = get_db()
    if db is not None and effective_user_id != "anonymous":
        try:
            now = now_utc()
            if is_new_conv:
                new_conv = {
                    "_id": ObjectId(effective_conv_id),
                    "userId": effective_user_id,
                    "title": file.filename,
                    "documentName": file.filename,
                    "language": language,
                    "documentUploaded": True,
                    "chunksCount": str(chunk_count),
                    "analysis": analysis,
                    "createdAt": now,
                    "updatedAt": now,
                }
                await db.conversations.insert_one(new_conv)
            else:
                await db.conversations.update_one(
                    {"_id": ObjectId(effective_conv_id), "userId": effective_user_id},
                    {
                        "$set": {
                            "documentName": file.filename,
                            "language": language,
                            "documentUploaded": True,
                            "chunksCount": str(chunk_count),
                            "analysis": analysis,
                            "updatedAt": now,
                        }
                    },
                )
        except Exception as db_exc:
            logger.warning(f"Failed to update conversation in MongoDB: {db_exc}")

    return {
        "message": "Document ingested",
        "filename": file.filename,
        "chunks": chunk_count,
        "chunks_created": chunk_count,
        "analysis": analysis,
        "conversationId": effective_conv_id,
    }


async def _resolve_document_name(doc_name: Optional[str], conv_id: Optional[str]) -> Optional[str]:
    if doc_name:
        return doc_name
    if not conv_id:
        return None
    db = get_db()
    if db is None:
        return None
    try:
        conv = await db.conversations.find_one({"_id": ObjectId(conv_id)})
        return conv.get("documentName") if conv else None
    except Exception:
        return None


@app.post("/api/ask", response_model=AskResponse)
@app.post("/ask", response_model=AskResponse)
async def ask_question(
    payload: AskRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
) -> AskResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    user_id = (current_user["id"] if current_user else None) or payload.get_user_id()
    conv_id = payload.get_conversation_id()
    document_name = await _resolve_document_name(payload.get_document_name(), conv_id)

    top_k = int(os.getenv("TOP_K", "4"))
    history = [
        {"role": item.role, "content": item.content}
        for item in payload.history
        if item.role in {"user", "assistant"}
    ]

    start_time = time.time()
    answer, citations = rag_engine.build_answer(
        question,
        top_k=top_k,
        language=payload.language,
        history=history,
        document_name=document_name,
        user_id=user_id or "anonymous",
        chat_id=conv_id or "default",
    )
    latency_ms = round((time.time() - start_time) * 1000, 2)
    now = now_utc()

    chat_id_str = "local-id"
    db = get_db()
    if db is not None:
        try:
            chat_doc = {
                "userId": user_id,
                "conversationId": conv_id,
                "question": question,
                "answer": answer,
                "latencyMs": latency_ms,
                "retrievalCount": len(citations),
                "streamed": False,
                "citations": citations,
                "error": None,
                "createdAt": now,
                "updatedAt": now,
            }
            res = await db.chats.insert_one(chat_doc)
            chat_id_str = str(res.inserted_id)

            if conv_id and user_id:
                await db.conversations.update_one(
                    {"_id": ObjectId(conv_id)},
                    {"$set": {"updatedAt": now}},
                )
        except Exception as db_exc:
            logger.warning(f"Failed to save chat to MongoDB: {db_exc}")

    return AskResponse(
        id=chat_id_str,
        conversationId=conv_id,
        question=question,
        answer=answer,
        citations=citations,
        latencyMs=latency_ms,
        createdAt=now.isoformat(),
    )


@app.post("/api/ask/stream")
@app.post("/ask/stream")
async def ask_question_stream(
    payload: AskRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
) -> StreamingResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    user_id = (current_user["id"] if current_user else None) or payload.get_user_id()
    conv_id = payload.get_conversation_id()
    document_name = await _resolve_document_name(payload.get_document_name(), conv_id)

    top_k = int(os.getenv("TOP_K", "4"))
    history = [
        {"role": item.role, "content": item.content}
        for item in payload.history
        if item.role in {"user", "assistant"}
    ]

    start_time = time.time()
    token_stream, citations = rag_engine.stream_answer(
        question,
        top_k=top_k,
        language=payload.language,
        history=history,
        document_name=document_name,
        user_id=user_id or "anonymous",
        chat_id=conv_id or "default",
    )

    async def event_generator():
        accumulated_answer = ""
        preview = json.dumps(
            {"type": "citations_preview", "citations": citations[:3]},
            ensure_ascii=False,
        )
        yield f"data: {preview}\n\n"

        for token in token_stream:
            accumulated_answer += token
            data = json.dumps({"type": "token", "token": token}, ensure_ascii=False)
            yield f"data: {data}\n\n"

        latency_ms = round((time.time() - start_time) * 1000, 2)
        done = json.dumps(
            {"type": "done", "citations": citations, "latencyMs": latency_ms},
            ensure_ascii=False,
        )
        yield f"data: {done}\n\n"

        db = get_db()
        if db is not None:
            try:
                now = now_utc()
                chat_doc = {
                    "userId": user_id,
                    "conversationId": conv_id,
                    "question": question,
                    "answer": accumulated_answer,
                    "latencyMs": latency_ms,
                    "retrievalCount": len(citations),
                    "streamed": True,
                    "citations": citations,
                    "error": None,
                    "createdAt": now,
                    "updatedAt": now,
                }
                await db.chats.insert_one(chat_doc)
                if conv_id and user_id:
                    await db.conversations.update_one(
                        {"_id": ObjectId(conv_id)},
                        {"$set": {"updatedAt": now}},
                    )
            except Exception as db_exc:
                logger.warning(f"Failed to persist streamed chat to MongoDB: {db_exc}")

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/documents", response_model=list[DocumentInfo])
@app.get("/documents", response_model=list[DocumentInfo])
def list_documents() -> list[DocumentInfo]:
    return []


@app.delete("/api/documents/{filename}")
@app.delete("/documents/{filename}")
def delete_document(filename: str) -> dict:
    return {"message": "Document deleted", "filename": filename}


# Optional: Serve built Frontend SPA for Hugging Face Spaces / single container deployment
_static_candidates = [
    Path.cwd() / "static",
    Path(__file__).resolve().parent.parent.parent / "static",
    Path(__file__).resolve().parent.parent.parent.parent / "static",
    Path(__file__).resolve().parent.parent / "static",
    Path("/home/user/app/static"),
    Path("/app/static"),
    Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "client" / "dist",
]
_static_dir = next((c for c in _static_candidates if c.exists() and (c / "index.html").exists()), None)
if _static_dir:
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    if (_static_dir / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(_static_dir / "assets")), name="assets")

    @app.get("/")
    def serve_spa_root():
        return FileResponse(_static_dir / "index.html")

    @app.get("/{full_path:path}")
    def serve_spa_fallback(full_path: str):
        target = _static_dir / full_path
        if target.exists() and target.is_file():
            return FileResponse(target)
        return FileResponse(_static_dir / "index.html")
