"""Simplified chat agent."""
import asyncio
import uuid
from typing import Optional

from agents import Agent, Runner, OpenAIChatCompletionsModel, SQLiteSession
from openai import AsyncOpenAI

from ..core import config, OLLAMA_BASE_URL, API_KEY, DATABASE_PATH


class ChatAgent:
    """Simple chat agent wrapper."""

    def __init__(self):
        self.session: Optional[SQLiteSession] = None
        self._create_agent()
        self.reset()

    def _create_agent(self):
        """Create the agent with current configuration."""
        model = OpenAIChatCompletionsModel(
            model=config.model,
            openai_client=AsyncOpenAI(
                base_url=OLLAMA_BASE_URL, 
                api_key=API_KEY
            ),
        )
        self.agent = Agent(
            name="Assistant",
            instructions=config.system_prompt,
            model=model,
        )

    def update_model(self, model_name: str):
        """Update the model."""
        config.model = model_name
        self._create_agent()
        self.reset()

    def update_system_prompt(self, system_prompt: str):
        """Update the system prompt."""
        config.system_prompt = system_prompt
        self._create_agent()

    def reset(self):
        """Reset conversation."""
        self.session = SQLiteSession(str(uuid.uuid4()), str(DATABASE_PATH))

    def load_session(self, session_id: str):
        """Load existing session."""
        self.session = SQLiteSession(session_id, str(DATABASE_PATH))

    async def get_response(self, prompt: str) -> str:
        """Get response from the agent."""
        try:
            result = await Runner.run(self.agent, prompt, session=self.session)
            return result.final_output
        except Exception as e:
            return f"Error: {e}"
