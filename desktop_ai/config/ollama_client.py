"""Ollama integration for listing available models."""
import asyncio
from typing import List
import ollama

async def get_available_models() -> List[str]:
	"""Get list of available models from Ollama.
    
	Returns:
		List of model names, or empty list if Ollama is not available.
	"""
	try:
		# Run ollama.list() in a thread since it's not async
		loop = asyncio.get_event_loop()
		response = await loop.run_in_executor(None, ollama.list)
        
		# Extract model names from the response
		models = []
		if hasattr(response, 'models') and response.models:
			for model in response.models:
				if hasattr(model, 'model'):
					models.append(model.model)
				elif isinstance(model, dict) and 'model' in model:
					models.append(model['model'])
        
		return sorted(models)
        
	except Exception:
		# If Ollama is not available or there's any error, return empty list
		return []

def get_available_models_sync() -> List[str]:
	"""Synchronous version of get_available_models for UI components.
    
	Returns:
		List of model names, or empty list if Ollama is not available.
	"""
	try:
		response = ollama.list()
        
		# Extract model names from the response
		models = []
		if hasattr(response, 'models') and response.models:
			for model in response.models:
				if hasattr(model, 'model'):
					models.append(model.model)
				elif isinstance(model, dict) and 'model' in model:
					models.append(model['model'])
        
		return sorted(models)
        
	except Exception:
		# If Ollama is not available or there's any error, return empty list
		return []
