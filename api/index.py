import sys
from pathlib import Path

# Add src/ to python module search path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from qa_chatbot.main import app

# Vercel serverless entrypoint
app = app
