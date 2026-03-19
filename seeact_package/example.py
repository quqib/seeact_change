import asyncio
import os
import litellm
from seeact.agent import SeeActAgent

# Setup your API Key here, or pass through environment
os.environ["OPENAI_API_KEY"] = "sk-djopgpiaqvbtecyekaqftozuxkkpartbhjygxbfdjuazwpkz"
# os.environ["GEMINI_API_KEY"] = "sk-djopgpiaqvbtecyekaqftozuxkkpartbhjygxbfdjuazwpkz"

# litellm.set_verbose = True

async def run_agent():
    agent = SeeActAgent(model="ByteDance-Seed/Seed-OSS-36B-Instruct")
    # agent = SeeActAgent(model="gpt-4o")
    await agent.start()
    while not agent.complete_flag:
        prediction_dict = await agent.predict()
        await agent.execute(prediction_dict)
    await agent.stop()

if __name__ == "__main__":
    asyncio.run(run_agent())
