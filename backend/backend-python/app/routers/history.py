from __future__ import annotations
import re
from typing import Optional
from fastapi import APIRouter, Query
from app.core.database import get_db

router = APIRouter(prefix="/api", tags=["analytics"])

@router.get("/history")
async def get_history(
    limit: int = Query(30, ge=1, le=100),
    q: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
):
    db = get_db()
    if db is None:
        return {"items": [], "count": 0}
    query: dict = {}
    if q and q.strip():
        safe_q = re.escape(q.strip())
        query["$or"] = [
            {"question": {"$regex": safe_q, "$options": "i"}},
            {"answer": {"$regex": safe_q, "$options": "i"}},
        ]
    if source and source.strip():
        query["citations.source"] = source.strip()

    cursor = db.chats.find(query).sort("createdAt", -1).limit(limit)
    items = []
    async for doc in cursor:
        items.append({
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
        })
    return {"items": items, "count": len(items)}

@router.get("/metrics")
async def get_metrics():
    db = get_db()
    if db is None:
        return {
            "totalChats": 0,
            "avgLatencyMs": 0,
            "avgRetrievalCount": "0.0",
            "streamedCount": 0,
        }
    total_chats = await db.chats.count_documents({})
    pipeline = [
        {
            "$group": {
                "_id": None,
                "avgLatencyMs": {"$avg": "$latencyMs"},
                "avgRetrievalCount": {"$avg": "$retrievalCount"},
                "streamedCount": {
                    "$sum": {"$cond": [{"$eq": ["$streamed", True]}, 1, 0]}
                },
            }
        }
    ]
    aggregate = await db.chats.aggregate(pipeline).to_list(1)
    stats = aggregate[0] if aggregate else {}
    avg_lat = stats.get("avgLatencyMs")
    avg_ret = stats.get("avgRetrievalCount")
    streamed = stats.get("streamedCount", 0)

    return {
        "totalChats": total_chats,
        "avgLatencyMs": round(float(avg_lat or 0)),
        "avgRetrievalCount": f"{float(avg_ret or 0):.1f}",
        "streamedCount": int(streamed or 0),
    }
