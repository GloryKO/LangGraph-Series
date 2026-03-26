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
MODEL_NAME: str = os.getenv("MODEL_NAME", "groq:llama-3.1-8b-instant")

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_JSON: bool = os.getenv("LOG_JSON", "false").lower() in ("true", "1", "yes")

# ── Retry settings ───────────────────────────────────────────────────────────
RETRY_MAX_ATTEMPTS: int = int(os.getenv("RETRY_MAX_ATTEMPTS", "3"))
RETRY_WAIT_SECONDS: float = float(os.getenv("RETRY_WAIT_SECONDS", "1.0"))

# ── API keys (read-only references for availability checks) ──────────────────
TAVILY_API_KEY: str | None = os.getenv("TAVILY_API_KEY")
OPENWEATHERMAP_API_KEY: str | None = os.getenv("OPENWEATHERMAP_API_KEY")
GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
