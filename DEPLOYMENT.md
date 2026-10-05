# 🚀 SahayakAI Production Deployment Guide

SahayakAI is packaged as a **production-ready containerized application** that runs the React frontend and FastAPI backend either as a **unified single container** or as **split microservices**.

---

## 🏗️ Deployment Architecture

```
[ Client Browser ]
       │  HTTP / HTTPS (Port 8000)
       ▼
┌────────────────────────────────────────────────────────┐
│  SahayakAI Docker Container                            │
│                                                        │
│  ├── Static UI: React + Vite SPA (mounted at /)        │
│  ├── API: FastAPI Router (mounted at /api/*)           │
│  │    ├── Auth & JWT                                   │
│  │    ├── MongoDB Persistence                          │
│  │    └── LangChain FAISS RAG Pipeline + SSE Stream    │
│  └── Storage:                                          │
│       ├── /app/uploads (Uploaded documents)            │
│       └── /app/vectorstore (FAISS vector indexes)      │
└──────────────┬─────────────────────────┬───────────────┘
               │                         │
               ▼                         ▼
     [ MongoDB Atlas / Mongo ]     [ Groq Cloud API ]
```

---

## ⚡ Option 1: Quickstart with Docker Compose (Recommended for Local & VPS)

This brings up SahayakAI along with persistent storage and an optional local MongoDB database.

### 1. Prepare Environment
Copy `.env.docker.example` to `.env` in the root directory:

```bash
cp .env.docker.example .env
```

Ensure your Groq API key is set in `.env`:
```env
GROQ_CHAT_API_KEY=gsk_...
GROQ_SUMMARY_API_KEY=gsk_...
JWT_SECRET=generate_a_random_secret_string
```

> **Note on MongoDB**: By default, `docker-compose.yml` connects to the included local `mongodb` container (`mongodb://mongodb:27017/sahayakai`). If you already have a **MongoDB Atlas** database, paste your connection string into `MONGO_URI` in `.env`.

### 2. Build and Start

```bash
docker compose up --build -d
```

### 3. Verify Health
- Open **http://localhost:8000** in your browser.
- Check API health: **http://localhost:8000/health**
- View logs: `docker compose logs -f app`

### 4. Stop Services
```bash
docker compose down
```
*(Data in `/app/uploads` and `/app/vectorstore` persists inside Docker volumes `sahayakai_uploads` and `sahayakai_vectorstore`).*

---

## ☁️ Option 2: Deploying to Cloud Platforms

Because the root `Dockerfile` is a self-contained multi-stage build, you can deploy it to any container hosting platform without modifying code.

### A. Deploy to Render (Render.com)

1. Push your repository to GitHub or GitLab.
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** > **Web Service**.
4. Connect your SahayakAI repository.
5. Configure the service:
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./Dockerfile`
   - **Instance Type**: Starter (at least 1GB RAM recommended for sentence-transformers).
6. Under **Disks** (optional, recommended for persistent vectorstore):
   - Add a persistent disk mounted at `/app/vectorstore` and `/app/uploads` (Size: 1 GB+).
7. Under **Environment Variables**, add:
   - `GROQ_CHAT_API_KEY`: your Groq key
   - `GROQ_SUMMARY_API_KEY`: your Groq key
   - `MONGO_URI`: your MongoDB Atlas connection string
   - `JWT_SECRET`: your secret key
   - `PORT`: `8000`
8. Click **Deploy Web Service**. Render will automatically build the React assets and launch FastAPI.

---

### B. Deploy to Railway (Railway.app)

1. In Railway, click **New Project** > **Deploy from GitHub repo**.
2. Select your SahayakAI repository.
3. Railway automatically detects the root `Dockerfile`.
4. In **Variables**, add:
   - `GROQ_CHAT_API_KEY`
   - `GROQ_SUMMARY_API_KEY`
   - `MONGO_URI`
   - `JWT_SECRET`
   - `PORT`: `8000`
5. In **Settings** > **Volumes**, add a volume mounted to `/app/vectorstore`.
6. Click **Generate Domain** under Networking. Your app will be live on `https://<your-domain>.up.railway.app`.

---

### C. Deploy to Fly.io

1. Install `flyctl` and log in:
   ```bash
   fly auth login
   ```
2. Initialize the app:
   ```bash
   fly launch --no-deploy
   ```
3. Set your environment secrets:
   ```bash
   fly secrets set GROQ_CHAT_API_KEY="your_key" GROQ_SUMMARY_API_KEY="your_key" MONGO_URI="mongodb+srv://..." JWT_SECRET="your_secret"
   ```
4. Create persistent volumes for vector storage:
   ```bash
   fly volumes create sahayakai_data --size 2
   ```
   Mount it in `fly.toml`:
   ```toml
   [mounts]
     source = "sahayakai_data"
     destination = "/app/vectorstore"
   ```
5. Deploy:
   ```bash
   fly deploy
   ```

---

### D. Deploy to a Linux VPS (Ubuntu / Debian / EC2 / DigitalOcean)

1. SSH into your VPS:
   ```bash
   ssh user@your-server-ip
   ```
2. Clone your repository:
   ```bash
   git clone <your-repo-url> sahayakai
   cd sahayakai
   ```
3. Create `.env` from template:
   ```bash
   cp .env.docker.example .env
   nano .env
   ```
4. Run with Docker Compose:
   ```bash
   docker compose up -d --build
   ```
5. Set up Caddy or Nginx for SSL (HTTPS) reverse-proxying port `8000`:
   ```caddyfile
   # Example Caddyfile (/etc/caddy/Caddyfile)
   sahayak.yourdomain.com {
       reverse_proxy 127.0.0.1:8000
   }
   ```

---

## ⚙️ Environment Variables Reference

| Variable | Required? | Default | Description |
| :--- | :--- | :--- | :--- |
| `GROQ_CHAT_API_KEY` | **Yes** | — | Groq API Key for answering queries and Vision OCR. |
| `GROQ_SUMMARY_API_KEY`| **Yes** | — | Groq API Key for document analysis/summaries. |
| `MONGO_URI` | **Yes** | `mongodb://mongodb:27017/sahayakai` | MongoDB connection string (Atlas or local). |
| `JWT_SECRET` | **Yes** | *fallback provided* | Secret key used to sign and verify user JWTs. |
| `PORT` | No | `8000` | Port uvicorn binds to inside container. |
| `GROQ_MODEL` | No | `openai/gpt-oss-120b` | Model used for chat and reasoning. |
| `VISION_MODEL` | No | `qwen/qwen3.8-27b` | Model used for vision OCR of images/scans. |
| `EMBEDDING_MODEL` | No | `paraphrase-multilingual-MiniLM-L12-v2` | Sentence transformer embeddings model. |
| `VECTOR_DB_DIR` | No | `/app/vectorstore` | Location where FAISS indexes are saved. |
| `UPLOAD_DIR` | No | `/app/uploads` | Location where user uploaded files are saved. |
| `FRONTEND_ORIGIN` | No | `http://localhost:5173,http://localhost:8000` | CORS allowed origins. |

---

## 🔒 Security Best Practices

1. **Keep Secrets Out of Images**: Never hardcode API keys or passwords in the `Dockerfile`. Use `.env` or cloud secret managers.
2. **Persistent Volumes**: Always mount `/app/vectorstore` and `/app/uploads` to persistent volumes so document indexes aren't lost upon container restart.
3. **HTTPS / TLS**: In production, always terminate SSL with a reverse proxy (Cloudflare, Caddy, Nginx, or cloud provider ingress).
