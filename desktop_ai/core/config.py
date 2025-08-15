"""Simple configuration management."""
import json
from typing import Dict, Any
from .constants import CONFIG_FILE, DEFAULT_MODEL, SYSTEM_INSTRUCTIONS


class Config:
    """Simple configuration class."""
    
    def __init__(self):
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        defaults = {
            "model": DEFAULT_MODEL,
            "system_prompt": SYSTEM_INSTRUCTIONS
        }
        
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                defaults.update(config)
            return defaults
        except Exception:
            return defaults
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Silently ignore save errors
    
    @property
    def model(self) -> str:
        return self._config.get('model', DEFAULT_MODEL)
    
    @model.setter
    def model(self, value: str) -> None:
        self._config['model'] = value
        self.save()
    
    @property
    def system_prompt(self) -> str:
        return self._config.get('system_prompt', SYSTEM_INSTRUCTIONS)
    
    @system_prompt.setter
    def system_prompt(self, value: str) -> None:
        self._config['system_prompt'] = value
        self.save()


# Global instance
config = Config()
