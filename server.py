"""
SahayakAI - Production Entry Point for Hugging Face Spaces & Cloud Platforms
Runs unified FastAPI + Pre-built React Frontend on Port 7860
"""
import os
import sys
from pathlib import Path

# Insert backend-python directory into sys.path
REPO_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = REPO_ROOT / "backend" / "backend-python"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Ensure current directory is not shadowing 'app'
if "app" in sys.modules and not hasattr(sys.modules["app"], "__path__"):
    del sys.modules["app"]

import uvicorn
from app.main import app

# Optional companion Gradio status page for HF Gradio SDK healthcheck probe
try:
    import gradio as gr

    with gr.Blocks(title="SahayakAI Status") as status_ui:
        gr.Markdown("## 🎓 SahayakAI Server is Online\nNavigate to `/` to use the interactive application.")

    app = gr.mount_gradio_app(app, status_ui, path="/gradio")
except Exception:
    pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"Starting SahayakAI on 0.0.0.0:{port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
