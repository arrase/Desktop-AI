"""Ollama service for managing local AI models."""

import asyncio
from typing import List
import ollama
import requests


class OllamaService:
    """Service for interacting with Ollama local AI models."""
    
    @staticmethod
    async def get_available_models() -> List[str]:
        """Get list of available models from Ollama asynchronously.

        Returns:
            List of model names, or empty list if Ollama is not available.
        """
        try:
            # Run ollama.list() in a thread since it's not async
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, ollama.list)
            return OllamaService._extract_model_names(response)
        except Exception:
            # If Ollama is not available or there's any error, return empty list
            return []

    @staticmethod
    def get_available_models_sync() -> List[str]:
        """Get list of available models from Ollama synchronously.

        Returns:
            List of model names, or empty list if Ollama is not available.
        """
        try:
            response = ollama.list()
            return OllamaService._extract_model_names(response)
        except Exception:
            # If Ollama is not available or there's any network/API error, return empty list
            return []
    
    @staticmethod
    def _extract_model_names(response) -> List[str]:
        """Extract model names from Ollama response."""
        models = []
        if hasattr(response, 'models') and response.models:
            for model in response.models:
                if hasattr(model, 'model'):
                    models.append(model.model)
                elif isinstance(model, dict) and 'model' in model:
                    models.append(model['model'])
        return sorted(models)
    
    @staticmethod
    def is_available() -> bool:
        """Check if Ollama is available and responding."""
        try:
            ollama.list()
            return True
        except Exception:
            return False
