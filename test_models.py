import os
import httpx
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import time

load_dotenv(os.path.join(os.path.dirname(__file__), 'backend2', '.env'))

models = [
    "azure/genailab-maas-gpt-35-turbo",
    "azure/genailab-maas-gpt-4o",
    "azure/genailab-maas-gpt-4o-mini",
    "azure_ai/genailab-maas-DeepSeek-R1",
    "azure_ai/genailab-maas-DeepSeek-V3-0324",
    "azure_ai/genailab-maas-Llama-3.3-70B-Instruct"
]

client = httpx.Client(verify=False)
api_key = os.environ.get("OPENAI_API_KEY")

print(f"Testing key: {api_key}")

for model in models:
    print(f"\nTesting model: {model}")
    llm = ChatOpenAI(
        base_url="https://genailab.tcs.in/v1",
        model=model,
        api_key=api_key,
        http_client=client
    )
    try:
        response = llm.invoke("Hi")
        print(f"SUCCESS with {model}: {response.content}")
        break
    except Exception as e:
        print(f"Failed with {model}: {e}")
    time.sleep(1)
