"""Chat agent abstraction over the `agents` library.

This keeps model + agent construction encapsulated and exposes a single
`get_response` coroutine. Future improvements (streaming, tool use,
error classification, retries, cancellation) can be centralized here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import asyncio

from agents import Agent, Runner, OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from ..core.config import get_config
from ..core.constants import DEFAULT_MODEL, OLLAMA_BASE_URL, API_KEY, SYSTEM_INSTRUCTIONS


@dataclass
class ChatAgentConfig:
    model: str = DEFAULT_MODEL
    base_url: str = OLLAMA_BASE_URL
    api_key: str = API_KEY
    system_instructions: str = SYSTEM_INSTRUCTIONS


class ChatAgent:
    """High level chat interface.

    A light wrapper to isolate external library surface from the UI layer.
    """

    def __init__(self, config: Optional[ChatAgentConfig] = None):
        self.config = config or ChatAgentConfig()
        # Use the selected model from config if no specific config is provided
        if config is None:
            self.config.model = get_config().selected_model

        self._create_agent()

    def _create_agent(self):
        """Create the agent with current configuration."""
        self.model = OpenAIChatCompletionsModel(
            model=self.config.model,
            openai_client=AsyncOpenAI(
                base_url=self.config.base_url, api_key=self.config.api_key
            ),
        )
        self.agent = Agent(
            name="Assistant",
            instructions=self.config.system_instructions,
            model=self.model,
        )

    def update_model(self, model_name: str):
        """Updates the model used by the agent."""
        self.config.model = model_name
        self._create_agent()

    async def get_response(self, prompt: str) -> str:
        """Return assistant reply for prompt.

        Captures exceptions and returns a user friendly message. In the
        future we could raise instead and let UI decide.
        """
        try:
            result = await Runner.run(self.agent, prompt)
            return result.final_output
        except Exception as e:  # broad: upstream lib may raise varied errors
            return f"Error: {e}"  # keep short; UI already labels assistant


async def _demo():  # pragma: no cover - manual test helper
    chat_agent = ChatAgent()
    print(await chat_agent.get_response("Ping?"))


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(_demo())
