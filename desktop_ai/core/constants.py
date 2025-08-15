"""Application constants."""
import os
from pathlib import Path

DEFAULT_MODEL = "gpt-oss:20b"
OLLAMA_BASE_URL = "http://localhost:11434/v1"
API_KEY = "sk-fake_api_key"
SYSTEM_INSTRUCTIONS = "You are a helpful assistant"

# Paths
CONFIG_DIR_NAME = ".config/desktop-ai"
CONFIG_FILE_NAME = "config.json"
CONVERSATION_DB_PATH = str(
    Path(os.path.expanduser("~")) / CONFIG_DIR_NAME / "conversations.db"
)
