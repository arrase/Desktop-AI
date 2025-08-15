"""Configuration management for Desktop AI application."""
import json
import threading
from pathlib import Path
from typing import Dict, Any
from .constants import DEFAULT_MODEL, CONFIG_DIR_NAME, CONFIG_FILE_NAME, SYSTEM_INSTRUCTIONS


class Config:
    """Centralized configuration management."""
    
    def __init__(self):
        self._config_dir = Path.home() / CONFIG_DIR_NAME
        self._config_file = self._config_dir / CONFIG_FILE_NAME
        self._config_data = self._load_config()
    
    @property
    def config_dir(self) -> Path:
        """Get the configuration directory, creating it if it doesn't exist."""
        self._config_dir.mkdir(parents=True, exist_ok=True)
        return self._config_dir
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file, return defaults if file doesn't exist."""
        defaults = {
            "model": DEFAULT_MODEL,
            "system_prompt": SYSTEM_INSTRUCTIONS
        }
        try:
            if self._config_file.exists():
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Ensure essential keys are present
                    if 'model' not in config:
                        config['model'] = defaults['model']
                    if 'system_prompt' not in config:
                        config['system_prompt'] = defaults['system_prompt']
                    return config
            else:
                return defaults
        except (json.JSONDecodeError, IOError):
            # If config file is corrupted or can't be read, return defaults
            return defaults
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            self.config_dir  # Ensure directory exists
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config_data, f, indent=2, ensure_ascii=False)
        except IOError:
            # Silently fail if we can't write config
            pass
    
    @property
    def selected_model(self) -> str:
        """Get the currently selected model from config."""
        return self._config_data.get('model', DEFAULT_MODEL)
    
    @selected_model.setter
    def selected_model(self, model: str) -> None:
        """Set the selected model in config."""
        self._config_data['model'] = model
        self.save()

    @property
    def system_prompt(self) -> str:
        """Get the currently configured system prompt."""
        return self._config_data.get('system_prompt', SYSTEM_INSTRUCTIONS)

    @system_prompt.setter
    def system_prompt(self, prompt: str) -> None:
        """Set the system prompt in config."""
        self._config_data['system_prompt'] = prompt
        self.save()
    
    def get(self, key: str, default=None):
        """Get a configuration value."""
        return self._config_data.get(key, default)
    
    def set(self, key: str, value) -> None:
        """Set a configuration value."""
        self._config_data[key] = value
        self.save()


# Global config instance with thread-safe initialization
_config_instance = None
_config_lock = threading.Lock()

def get_config() -> Config:
    """Get the global configuration instance (thread-safe singleton)."""
    global _config_instance
    
    # Double-checked locking pattern for thread-safe singleton
    if _config_instance is None:
        with _config_lock:
            # Check again inside the lock to prevent race condition
            if _config_instance is None:
                _config_instance = Config()
    
    return _config_instance
