"""Application constants."""
from pathlib import Path

# Models and API
DEFAULT_MODEL = "gpt-oss:20b"
OLLAMA_BASE_URL = "http://localhost:11434/v1"
API_KEY = "sk-fake_api_key"
SYSTEM_INSTRUCTIONS = "You are a helpful assistant"

# Configuration
CONFIG_DIR = Path.home() / ".config" / "desktop-ai"
CONFIG_FILE = CONFIG_DIR / "config.json"
DATABASE_PATH = CONFIG_DIR / "conversations.db"

# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
