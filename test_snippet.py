import os
import httpx
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'backend2', '.env'))

# Exactly copy the user's snippet
client = httpx.Client(verify=False)
llm = ChatOpenAI(
    base_url="https://genailab.tcs.in/v1",
    model="azure_ai/genailab-maas-DeepSeek-V3-0324",
    api_key=os.environ.get("OPENAI_API_KEY"),
    http_client=client
)

print(f"API Key being used: {os.environ.get('OPENAI_API_KEY')}")
print("Invoking Hi...")
try:
    response = llm.invoke("Hi")
    print("Success!")
    print(response.content)
except Exception as e:
    print(f"Error: {e}")
