"""Simplified Ollama service."""
import ollama
import logging
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
                for model_info in response.models:
                    models.append(model_info.model)
            return sorted(models)
        except Exception as e:
            logging.error(f"Error getting Ollama models: {e}")
            return []

    @staticmethod
    def is_available() -> bool:
        """Check if Ollama is available."""
        try:
            ollama.list()
            return True
        except Exception as e:
            logging.error(f"Error checking Ollama availability: {e}")
            return False
