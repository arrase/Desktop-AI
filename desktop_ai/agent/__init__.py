"""Agent package exposing ChatAgent and configuration.

Placed directly in __init__ to simplify import resolution.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from agents import Agent, Runner, OpenAIChatCompletionsModel

try:
	# Newer versions may expose AsyncOpenAI publicly
	from agents import AsyncOpenAI  # type: ignore
except Exception:  # pragma: no cover
	AsyncOpenAI = None  # type: ignore

_DEFAULT_MODEL = "gpt-oss:20b"
_DEFAULT_BASE_URL = "http://localhost:11434/v1"


@dataclass
class ChatAgentConfig:
	model: str = _DEFAULT_MODEL
	base_url: str = _DEFAULT_BASE_URL
	api_key: str = "sk-fake_api_key"
	system_instructions: str = "You are a helpful assistant"


class ChatAgent:
	def __init__(self, config: Optional[ChatAgentConfig] = None):
		self.config = config or ChatAgentConfig()
		if AsyncOpenAI is None:
			raise RuntimeError("AsyncOpenAI no disponible en la versión instalada de 'agents'. Actualiza el paquete o ajusta la implementación.")
		self.model = OpenAIChatCompletionsModel(
			model=self.config.model,
			openai_client=AsyncOpenAI(base_url=self.config.base_url, api_key=self.config.api_key),
		)
		self.agent = Agent(
			name="Assistant",
			instructions=self.config.system_instructions,
			model=self.model,
		)

	async def get_response(self, prompt: str) -> str:
		try:
			result = await Runner.run(self.agent, prompt)
			return result.final_output
		except Exception as e:
			return f"Error: {e}"

from .chat_agent import ChatAgent, ChatAgentConfig
__all__ = ["ChatAgent", "ChatAgentConfig"]