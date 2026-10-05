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
# Configured for Hugging Face Spaces (UID 1000, Port 7860) & Cloud
# ==========================================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1

# Install system dependencies:
# - curl: healthchecks
# - libgomp1: required by FAISS CPU on Linux
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face Spaces requirement: run as non-root user with UID 1000
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    HF_HOME=/home/user/.cache/huggingface \
    VECTOR_DB_DIR=/home/user/app/vectorstore \
    UPLOAD_DIR=/home/user/app/uploads

WORKDIR /home/user/app

# Install Python dependencies
COPY backend/backend-python/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Pre-cache the HuggingFace embedding model at build time for instant cold starts
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"

# Copy backend application source
COPY --chown=user:user backend/backend-python/app /home/user/app/app

# Copy built frontend assets into static directory (FastAPI mounts this at / automatically)
COPY --chown=user:user --from=frontend-builder /build/dist /home/user/app/static

# Create persistent storage directories and assign permissions to user 1000
RUN mkdir -p /home/user/app/vectorstore /home/user/app/uploads && \
    chown -R user:user /home/user

USER user

EXPOSE 7860

HEALTHCHECK --interval=15s --timeout=5s --start-period=15s --retries=3 \
    CMD curl --fail http://localhost:${PORT:-7860}/health || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
