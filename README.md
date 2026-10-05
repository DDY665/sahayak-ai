---
title: SahayakAI
emoji: 🎓
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: 5.20.0
app_file: server.py
pinned: false
---

# SahayakAI (Unified Multimodal Document AI & RAG)

SahayakAI is an intelligent document Q&A and analysis system powered by Groq (Llama 3.3 70B), LangChain, HuggingFace Multilingual Embeddings, FAISS vector search, and a modern React + Tailwind UI.

## Free Deployment Options ($0 Cost)

### Option 1: Hugging Face Spaces (Gradio SDK - Free CPU 16GB RAM)
1. Go to [Hugging Face Spaces](https://huggingface.co/new-space).
2. Space Name: `sahayakai`.
3. Select **Space SDK**: Choose **Gradio** (NOT Docker — Gradio is **100% Free** with 16GB RAM).
4. Select **Space Hardware**: **CPU basic · 2 vCPU · 16 GB · FREE**.
5. Create the Space.
6. Push this repository to your Space:
   ```bash
   git remote add hf https://huggingface.co/spaces/<YOUR_USERNAME>/sahayakai
   git push hf main
   ```
7. In your Space's **Settings > Variables and secrets**, add these Secrets:
   - `GROQ_CHAT_API_KEY`: your Groq API key
   - `GROQ_SUMMARY_API_KEY`: your Groq API key (or secondary key)
   - `MONGO_URI`: your MongoDB Atlas connection string (Free M0 cluster)
   - `JWT_SECRET`: any secure random string

### Option 2: Render.com (Free Native Python Web Service)
1. Push your repository to GitHub.
2. Sign in to [Render.com](https://render.com) (free, no credit card required).
3. Click **New + > Web Service**.
4. Connect your GitHub repository.
5. Configure:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
   - **Plan**: Free ($0/month)
6. Add your Environment Secrets in the Render dashboard (`GROQ_CHAT_API_KEY`, `MONGO_URI`, `JWT_SECRET`).
7. Click **Create Web Service**.

---

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Server
```bash
python server.py
```
Open `http://localhost:7860` to access the full application and React UI.

---

## Environment Variables
- `GROQ_CHAT_API_KEY`: Groq API Key for conversation answering & OCR.
- `GROQ_SUMMARY_API_KEY`: Groq API Key for document analysis & key takeaways.
- `MONGO_URI`: MongoDB connection string for users, sessions, and chat history.
- `JWT_SECRET`: Secret key for JWT authentication tokens.
- `PORT`: Server port (default: `7860`).
