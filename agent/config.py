"""Configuration — centralised settings loaded from .env."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# ── Paths ────────────────────────────────────────────────────────────────────
DATA_DIR = _PROJECT_ROOT / "data"
DB_PATH = str(DATA_DIR / "local_info.db")
EVENTS_JSON_PATH = str(DATA_DIR / "events_db.json")

# ── Model ────────────────────────────────────────────────────────────────────
MODEL_NAME: str = os.getenv("MODEL_NAME", "google_genai:gemini-2.0-flash")

# ── API keys (read-only references for availability checks) ──────────────────
TAVILY_API_KEY: str | None = os.getenv("TAVILY_API_KEY")
OPENWEATHERMAP_API_KEY: str | None = os.getenv("OPENWEATHERMAP_API_KEY")
GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
