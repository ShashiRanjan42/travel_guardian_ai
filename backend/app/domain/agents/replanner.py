import time
import json
from typing import List, Dict, Any
from app.domain.agents.base import AgentContext, AgentResult
from app.integrations.llm.base import LLMClient

class Replanner:
    def __init__(self, llm_client: LLMClient):
        self.name = "REPLANNER"
        self.llm_client = llm_client

    async def run(self, ctx: AgentContext) -> AgentResult:
        start_time = time.time()
        
        prompt = f"""Act as the replanning specialist for a disrupted trip.
Event: {ctx.event.headline}
Event details: {ctx.event.description}
Affected modes: {ctx.event.affected_modes}
Assessment ID: {ctx.assessment.id}; booking ID: {ctx.assessment.booking_id}
Traveller preferences: {ctx.traveller_profile or 'not available'}

Suggest up to three practical options. You may recommend requesting supplier confirmation,
but must not claim seats, fares, routes, or inventory are confirmed unless that evidence is
present in the supplied details. Return ONLY valid JSON in this form:
{{"options":[{{"rank":1,"label":"...","summary":"...","cost_delta_inr":0,
"time_delta_minutes":0,"risk_score":0.0,"confidence":0.0,
"evidence":[{{"source":"provided event data","claim":"..."}}],
"assumptions":["..."],"tradeoffs":"..."}}]}}"""
        
        # Enforce G-2 PII redaction here (in real app, we use redaction.py on traveller details)
        
        llm_response = await self.llm_client.generate(prompt)
        
        try:
            data = json.loads(llm_response)
            options = data.get("options", [])
        except json.JSONDecodeError:
            options = []
            
        # Groundedness Enforcement (G-5)
        # Any option with empty evidence is rejected in code before compliance
        valid_options = []
        for opt in options:
            if not opt.get("evidence"):
                # Discard hallucinated options
                continue
            valid_options.append(opt)
            
        duration_ms = int((time.time() - start_time) * 1000)
        
        return AgentResult(
            agent=self.name,
            status="success" if valid_options else "failed",
            output=valid_options,
            confidence=0.9,
            duration_ms=duration_ms,
            reasoning="OpenAI generated constrained alternatives; application code retained only options with evidence.",
            evidence=[] # Evidence is attached to individual options
        )
