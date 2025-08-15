"""Configuration management for Desktop AI application."""
import os
import json
from pathlib import Path
from typing import Dict, Any

_DEFAULT_MODEL = "gpt-oss:20b"
_CONFIG_DIR = Path.home() / ".config" / "desktop-ai"
_CONFIG_FILE = _CONFIG_DIR / "config.json"


def get_config_dir() -> Path:
    """Get the configuration directory, creating it if it doesn't exist."""
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return _CONFIG_DIR


def load_config() -> Dict[str, Any]:
    """Load configuration from file, return defaults if file doesn't exist."""
    try:
        if _CONFIG_FILE.exists():
            with open(_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Ensure we have a model key
                if 'model' not in config:
                    config['model'] = _DEFAULT_MODEL
                return config
        else:
            return {"model": _DEFAULT_MODEL}
    except (json.JSONDecodeError, IOError):
        # If config file is corrupted or can't be read, return defaults
        return {"model": _DEFAULT_MODEL}


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    try:
        get_config_dir()  # Ensure directory exists
        with open(_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except IOError:
        # Silently fail if we can't write config
        pass


def get_selected_model() -> str:
    """Get the currently selected model from config."""
    config = load_config()
    return config.get('model', _DEFAULT_MODEL)


def set_selected_model(model: str) -> None:
    """Set the selected model in config."""
    config = load_config()
    config['model'] = model
    save_config(config)
