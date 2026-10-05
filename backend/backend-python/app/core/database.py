from __future__ import annotations

import os
from typing import Optional
import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.logging_utils import configure_logging

logger = configure_logging()

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def connect_db() -> Optional[AsyncIOMotorDatabase]:
    global _client, _db
    if _db is not None:
        return _db

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        logger.warning("MONGO_URI not configured. Operating without database persistence.")
        return None

    try:
        # Use certifi CA bundle to ensure valid TLS handshake on Linux containers
        # Use 5000ms timeout so startup never hangs
        client_kwargs = {
            "serverSelectionTimeoutMS": 5000,
            "tlsCAFile": certifi.where(),
        }
        _client = AsyncIOMotorClient(mongo_uri, **client_kwargs)
        db_name = "sahayakai"
        if "/" in mongo_uri:
            parsed = mongo_uri.split("/")[-1].split("?")[0]
            if parsed:
                db_name = parsed
        _db = _client[db_name]

        await _db.users.create_index("email", unique=True)
        await _db.conversations.create_index("userId")
        await _db.chats.create_index("userId")
        await _db.chats.create_index("conversationId")

        logger.info(f"MongoDB connected successfully to database: {db_name}")
        return _db
    except Exception as exc:
        logger.warning(
            f"MongoDB connection failed: {exc}. "
            "Please check MongoDB Atlas Network Access (allow 0.0.0.0/0). "
            "Continuing server startup..."
        )
        return None


async def close_db() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB connection closed.")


def get_db() -> Optional[AsyncIOMotorDatabase]:
    return _db
