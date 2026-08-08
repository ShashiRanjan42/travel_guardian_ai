import asyncio
import os
import sys

# Add backend2 to sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend2')))

from app.integrations.llm.openai_responses import OpenAIResponsesClient

async def main():
    print("Testing connection to TCS GenAI Lab...")
    
    client_wrapper = OpenAIResponsesClient()
    llm = client_wrapper.get_client()
    
    print(f"Base URL configured as: {llm.model_dump().get('base_url', 'NOT SET')}")
    print(f"Model configured as: {llm.model_name}")
    
    try:
        print("\nSending: llm.invoke('Hi')")
        response = await llm.ainvoke("Hi")
        print("Success! Response:")
        print(response.content)
    except Exception as e:
        print("\nFailed! Here is the error:")
        print(e)

if __name__ == "__main__":
    asyncio.run(main())
