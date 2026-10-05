# ==========================================
# Stage 1: Build Frontend (React + Vite)
# ==========================================
FROM node:20-alpine AS frontend-builder

WORKDIR /build

COPY frontend/client/package*.json ./
RUN npm ci

COPY frontend/client/ ./
# Build frontend with relative API path (served by same container origin)
ENV VITE_API_BASE_URL=""
RUN npm run build

# ==========================================
# Stage 2: Production Runtime (FastAPI Backend)
# ==========================================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HF_HOME=/root/.cache/huggingface \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    VECTOR_DB_DIR=/app/vectorstore \
    UPLOAD_DIR=/app/uploads

# Install system dependencies:
# - curl: container healthcheck
# - libgomp1: required by FAISS CPU on Linux
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/backend-python/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Pre-cache the HuggingFace embedding model at build time for instant cold starts and offline execution
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"

# Copy backend application source
COPY backend/backend-python/app /app/app

# Copy built frontend assets into /app/static (FastAPI mounts this at / automatically)
COPY --from=frontend-builder /build/dist /app/static

# Create persistent storage directories
RUN mkdir -p /app/vectorstore /app/uploads

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=15s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
