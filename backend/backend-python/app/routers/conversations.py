from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from bson import ObjectId
from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.logging_utils import configure_logging
from app.models import now_utc

logger = configure_logging()
router = APIRouter(prefix="/api/conversations", tags=["conversations"])

class CreateConversationRequest(BaseModel):
    title: Optional[str] = "New Chat"
    documentName: Optional[str] = None

def _format_conversation(doc: dict) -> dict:
    return {
        "_id": str(doc["_id"]),
        "id": str(doc["_id"]),
        "userId": str(doc.get("userId", "")),
        "title": doc.get("title", "New Chat"),
        "documentName": doc.get("documentName"),
        "language": doc.get("language", "English"),
        "documentUploaded": doc.get("documentUploaded", False),
        "chunksCount": doc.get("chunksCount", "—"),
        "analysis": doc.get("analysis"),
        "createdAt": doc.get("createdAt").isoformat() if doc.get("createdAt") else None,
        "updatedAt": doc.get("updatedAt").isoformat() if doc.get("updatedAt") else None,
    }

def _format_chat(doc: dict) -> dict:
    return {
        "_id": str(doc["_id"]),
        "id": str(doc["_id"]),
        "userId": str(doc.get("userId")) if doc.get("userId") else None,
        "conversationId": str(doc.get("conversationId")) if doc.get("conversationId") else None,
        "question": doc.get("question", ""),
        "answer": doc.get("answer", ""),
        "latencyMs": doc.get("latencyMs"),
        "retrievalCount": doc.get("retrievalCount", 0),
        "streamed": doc.get("streamed", False),
        "citations": doc.get("citations", []),
        "error": doc.get("error"),
        "createdAt": doc.get("createdAt").isoformat() if doc.get("createdAt") else None,
    }

@router.get("")
async def list_conversations(current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        return {"conversations": []}
    user_id = current_user["id"]
    cursor = db.conversations.find({"userId": user_id}).sort("updatedAt", -1).limit(50)
    items = []
    async for doc in cursor:
        items.append(_format_conversation(doc))
    return {"conversations": items}

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: CreateConversationRequest,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    user_id = current_user["id"]
    now = now_utc()
    title = (payload.title or "New Chat").strip()
    conv_doc = {
        "userId": user_id,
        "title": title,
        "documentName": payload.documentName.strip() if payload.documentName else None,
        "language": "English",
        "documentUploaded": False,
        "chunksCount": "—",
        "analysis": None,
        "createdAt": now,
        "updatedAt": now,
    }
    result = await db.conversations.insert_one(conv_doc)
    conv_doc["_id"] = result.inserted_id
    logger.info(f"New conversation created: id={result.inserted_id}, userId={user_id}")
    return {"conversation": _format_conversation(conv_doc)}

@router.get("/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    user_id = current_user["id"]
    try:
        conv = await db.conversations.find_one({"_id": ObjectId(conversation_id), "userId": user_id})
    except Exception:
        conv = None
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    cursor = db.chats.find({"conversationId": conversation_id}).sort("createdAt", 1)
    messages = []
    async for doc in cursor:
        messages.append(_format_chat(doc))
    return {
        "conversation": _format_conversation(conv),
        "messages": messages,
    }

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    user_id = current_user["id"]
    try:
        result = await db.conversations.delete_one({"_id": ObjectId(conversation_id), "userId": user_id})
    except Exception:
        result = None
    if not result or result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await db.chats.delete_many({"conversationId": conversation_id})
    logger.info(f"Conversation deleted: id={conversation_id}, userId={user_id}")
    return {
        "message": "Conversation deleted successfully",
        "conversationId": conversation_id,
    }
