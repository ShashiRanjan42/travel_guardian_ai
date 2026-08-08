from typing import Protocol, Dict, Any, Optional

class LLMClient(Protocol):
    async def generate(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> str:
        ...
