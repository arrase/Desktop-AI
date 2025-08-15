"""Simplified Ollama service."""
import ollama
from typing import List


class OllamaService:
    """Service for Ollama model management."""
    
    @staticmethod
    def get_models() -> List[str]:
        """Get available models."""
        try:
            response = ollama.list()
            models = []
            if hasattr(response, 'models') and response.models:
                for model in response.models:
                    if hasattr(model, 'model'):
                        models.append(model.model)
                    elif isinstance(model, dict) and 'model' in model:
                        models.append(model['model'])
            return sorted(models)
        except Exception:
            return []
    
    @staticmethod
    def is_available() -> bool:
        """Check if Ollama is available."""
        try:
            ollama.list()
            return True
        except Exception:
            return False
