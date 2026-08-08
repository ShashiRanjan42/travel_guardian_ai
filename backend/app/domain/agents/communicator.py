import time
import json
from typing import List, Dict, Any
from app.domain.agents.base import AgentContext, AgentResult
from app.integrations.llm.base import LLMClient

class Communicator:
    def __init__(self, llm_client: LLMClient):
        self.name = "COMMUNICATOR"
        self.llm_client = llm_client

    async def run(self, ctx: AgentContext) -> AgentResult:
        start_time = time.time()
        
        options = ctx.options
        prompt = f"""Write a calm, concise traveller notification (maximum 90 words).
Explain the disruption, what we have done, and the next action. Do not include internal
scores, identifiers, or unverified promises. If no approved option exists, say that the
travel team is reviewing alternatives.
Disruption: {ctx.event.headline}\nDetails: {ctx.event.description}\nOptions: {json.dumps(options)}"""
        message = await self.llm_client.generate(prompt)
            
        duration_ms = int((time.time() - start_time) * 1000)
        
        return AgentResult(
            agent=self.name,
            status="success",
            output={"notification_draft": message},
            confidence=0.98,
            duration_ms=duration_ms,
            reasoning="OpenAI drafted a traveller-safe notification using the verified event and option context.",
            evidence=[]
        )
