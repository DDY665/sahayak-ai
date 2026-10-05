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

# ZeroGPU Compatibility: If the Space was launched on ZeroGPU hardware,
# register a dummy @spaces.GPU hook so ZeroGPU supervisor does not trigger a shutdown.
try:
    import spaces

    @spaces.GPU
    def _zero_gpu_keepalive():
        return True

    _zero_gpu_keepalive()
except Exception:
    pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"Starting SahayakAI on 0.0.0.0:{port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
