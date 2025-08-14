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
from agents._client import AsyncOpenAI  # type: ignore  # upstream private import

_DEFAULT_MODEL = "gpt-oss:20b"
_DEFAULT_BASE_URL = "http://localhost:11434/v1"


@dataclass
class ChatAgentConfig:
    model: str = _DEFAULT_MODEL
    base_url: str = _DEFAULT_BASE_URL
    api_key: str = "sk-fake_api_key"  # placeholder; allow override via env later
    system_instructions: str = "You are a helpful assistant"


class ChatAgent:
    """High level chat interface.

    A light wrapper to isolate external library surface from the UI layer.
    """

    def __init__(self, config: Optional[ChatAgentConfig] = None):
        self.config = config or ChatAgentConfig()
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
