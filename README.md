---
title: SahayakAI
emoji: 🩺
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# SahayakAI (Multilingual Document Intelligence & RAG Assistant)

SahayakAI is an AI-powered document intelligence and question-answering assistant for medical records, bank/financial statements, and government documents.

## Current Architecture

1. **Frontend (`frontend/client`)**: React + Vite SPA. Supports upload, structured document analysis, interactive quiz/Q&A, voice input, streaming markdown responses, and citations.
2. **Backend (`backend/backend-python`)**: Unified FastAPI 2.0 service. Directly manages JWT authentication, MongoDB persistence (conversations and chat history), multilingual FAISS vector storage, and Groq LLM inference with SSE streaming.

---

## Quickstart (Local Development)

### 1. Start Python Backend

```bash
cd backend/backend-python
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Start React Frontend

```bash
cd frontend/client
npm install
npm run dev
```

Open `http://localhost:5173`.

---

## 🚀 Production Deployment (Hugging Face Spaces & Docker)

SahayakAI is pre-configured for **100% free deployment on Hugging Face Spaces**:

1. Create a new Space on [Hugging Face](https://huggingface.co/new-space) with SDK **Docker**.
2. In Space **Settings** > **Variables and secrets**, add:
   - `GROQ_CHAT_API_KEY`: your Groq API key
   - `GROQ_SUMMARY_API_KEY`: your Groq API key
   - `MONGO_URI`: your MongoDB Atlas connection string
   - `JWT_SECRET`: your secret random key
3. Push this repository to your Space Git remote:
   ```bash
   git remote add hf https://huggingface.co/spaces/<your-username>/sahayakai
   git push hf main
   ```

For detailed deployment guides including Docker Compose, Render, and VPS, see [DEPLOYMENT.md](file:///d:/VS/SahayakAI/DEPLOYMENT.md).

---

## API Surface

- `GET /health`: Health check
- `POST /api/auth/register`: User registration
- `POST /api/auth/login`: User login (returns JWT token)
- `GET /api/auth/me`: Current user profile
- `GET /api/conversations`: List user conversations
- `POST /api/conversations`: Create conversation
- `POST /api/upload`: Upload and index document (session-scoped)
- `POST /api/ask`: Grounded question-answering
- `POST /api/ask/stream`: Real-time SSE streaming answer
- `GET /api/history`: Persistent chat history
- `GET /api/metrics`: Chat and document usage statistics
