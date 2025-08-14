from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI
import asyncio

class ChatAgent:
    def __init__(self):
        # Configure the model
        self.model = OpenAIChatCompletionsModel( 
            model="gpt-oss:20b",
            openai_client=AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="sk-fake_api_key")
        )

        # Create the agent
        self.agent = Agent(
            name="Assistant",
            instructions="You are a helpful assistant",
            model=self.model
        )

    async def get_response(self, prompt: str) -> str:
        # Run the agent
        try:
            result = await Runner.run(self.agent, prompt)
            return result.final_output
        except Exception as e:
            return f"An error occurred: {e}"

async def main():
    # Example usage
    chat_agent = ChatAgent()
    response = await chat_agent.get_response("Create a meal plan for a week.")
    print(response)

if __name__ == '__main__':
    asyncio.run(main())