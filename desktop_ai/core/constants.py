"""Application constants."""
from pathlib import Path

# Models and API
OLLAMA_BASE_URL = "http://localhost:11434/v1"
API_KEY = "sk-fake_api_key"
SYSTEM_INSTRUCTIONS = "You are a helpful assistant"

# Configuration
CONFIG_DIR = Path.home() / ".config" / "desktop-ai"
CONFIG_FILE = CONFIG_DIR / "config.json"
DATABASE_PATH = CONFIG_DIR / "conversations.db"
LOG_FILE = CONFIG_DIR / "desktop_ai.log"

# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
