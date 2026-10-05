from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from bson import ObjectId
from app.core.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.core.database import get_db
from app.core.logging_utils import configure_logging
from app.models import now_utc

logger = configure_logging()
router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    name = payload.name.strip()
    email = payload.email.strip().lower()
    password = payload.password.strip()

    if len(name) < 2:
        raise HTTPException(status_code=400, detail="Name must be at least 2 characters")
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Please provide a valid email address")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    existing_user = await db.users.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    hashed_pw = hash_password(password)
    now = now_utc()
    new_user = {
        "name": name,
        "email": email,
        "password": hashed_pw,
        "createdAt": now,
        "updatedAt": now,
    }
    result = await db.users.insert_one(new_user)
    user_id = str(result.inserted_id)

    token = create_access_token(user_id=user_id, email=email, name=name)
    logger.info(f"New user registered: id={user_id}, email={email}")

    return {
        "user": {"id": user_id, "name": name, "email": email},
        "token": token,
    }

@router.post("/login")
async def login(payload: LoginRequest):
    email = payload.email.strip().lower()
    password = payload.password.strip()

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user["_id"])
    token = create_access_token(user_id=user_id, email=email, name=user.get("name", ""))
    logger.info(f"User logged in: id={user_id}, email={email}")

    return {
        "user": {"id": user_id, "name": user.get("name", ""), "email": email},
        "token": token,
    }

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}
