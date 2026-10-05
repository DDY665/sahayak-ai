# Migration Plan: Consolidating SahayakAI to Full Python (Option 2)

This document tracks all tasks required to migrate SahayakAI from the 3-tier architecture (React -> Node -> Python) to a streamlined 2-tier architecture (React -> FastAPI).

---

## 🎯 Goal
Eliminate `backend/server-node` completely. Run a single backend service in Python (`FastAPI`), directly handling:
- User Authentication (JWT + bcrypt)
- MongoDB Persistence (Conversations, Chats, Metrics)
- Document Uploads & Storage
- RAG Pipeline (Embeddings, FAISS, Groq LLM, SSE Streaming)

Frontend (`frontend/client`) talks directly to FastAPI on port `8000`.

---

## 📋 Task Checklist

### Phase 1: Python Dependencies & Database Layer
- [x] **Task 1.1: Add Database & Auth Dependencies to Python**
  - Added `motor>=3.7.0`, `pyjwt>=2.8.0`, `bcrypt>=4.0.0` to `requirements.txt`.
- [x] **Task 1.2: Environment Configuration**
  - Added `MONGO_URI`, `JWT_SECRET`, `PORT=8000` to `.env` and `.env.example`.
- [x] **Task 1.3: Database Connection & Models**
  - Created `app/core/database.py` with async connection management and indexing.
  - Created `app/models.py` with schemas for `User`, `Conversation`, and `Chat`.

---

### Phase 2: Auth & User Management in FastAPI
- [x] **Task 2.1: Auth Utilities & Security Middleware**
  - Implemented `app/core/auth.py` with bcrypt hashing, JWT issuance/decoding, and `get_current_user` / `get_optional_user` dependencies.
- [x] **Task 2.2: Auth Endpoints**
  - Implemented `app/routers/auth.py` with `POST /api/auth/register`, `POST /api/auth/login`, and `GET /api/auth/me`.

---

### Phase 3: Conversation & Chat History Endpoints
- [x] **Task 3.1: Conversation Management Endpoints**
  - Implemented `app/routers/conversations.py` with `GET /api/conversations`, `POST /api/conversations`, `GET /api/conversations/{id}/messages`, `DELETE /api/conversations/{id}`.
- [x] **Task 3.2: History & Metrics Endpoints**
  - Implemented `app/routers/history.py` with `GET /api/history` and `GET /api/metrics`.

---

### Phase 4: Consolidate Document Ingestion & RAG Chat
- [x] **Task 4.1: Harmonize Upload & Document Management**
  - Consolidated `POST /api/upload` and `/ingest` into `app/main.py`.
  - Added session-scoped directory handling and automatic MongoDB conversation record updates.
- [x] **Task 4.2: Chat & Streaming with Persistence**
  - Consolidated `POST /api/ask` and `POST /api/ask/stream` with direct MongoDB chat storage and SSE token streaming.
  - Fixed offline HuggingFace embedding loading (`HF_HUB_OFFLINE=1`, `local_files_only=True`) to drop server startup time from 30+ seconds to under 2 seconds.
  - Updated Groq model configuration to active `openai/gpt-oss-120b` endpoint.

---

### Phase 5: Frontend Alignment
- [x] **Task 5.1: Update Frontend API Configuration**
  - Updated `frontend/client/src/config/constants.js` to point `API_BASE_URL` directly to `http://localhost:8000`.
- [x] **Task 5.2: CORS & Origin Setup**
  - Configured FastAPI CORS to allow `http://localhost:5173` with credentials, headers, and methods.

---

### Phase 6: Decommission Node & Clean Up
- [x] **Task 6.1: Verification & End-to-End Testing**
  - Verified `/health`, `/api/upload`, and live streaming `/api/ask/stream` responses via Groq.
- [x] **Task 6.2: Archive / Remove `backend/server-node`**
  - Deleted `backend/server-node` and obsolete audit files.
