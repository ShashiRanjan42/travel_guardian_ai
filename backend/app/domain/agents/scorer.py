import time
from typing import Dict, Any
from app.domain.scoring import calculate_severity
from app.domain.agents.base import AgentContext, AgentResult
from app.integrations.llm.base import LLMClient

class Scorer:
    def __init__(self, llm_client: LLMClient | None = None):
        self.name = "SCORER"
        self.llm_client = llm_client

    async def run(self, ctx: AgentContext) -> AgentResult:
        start_time = time.time()
        
        # We need to extract variables for scoring
        # Impact: simplified mock calculation based on affected modes / radius
        event = ctx.event
        impact_score = 15.0 # Base impact
        if event.radius_km > 20:
            impact_score += 10
        if len(event.affected_modes) > 1:
            impact_score += 5
            
        booking = ctx.assessment.booking if hasattr(ctx.assessment, "booking") else None
        hours_to_departure = ctx.assessment.hours_to_departure if hasattr(ctx.assessment, "hours_to_departure") else 14.2
        
        financial = booking.non_refundable_value_inr if booking else 16400
        vulnerability_flag = ctx.traveller_profile.get("vulnerability_flag", "none") if ctx.traveller_profile else "none"
            
        severity = calculate_severity(
            impact_score=impact_score,
            hours_to_departure=hours_to_departure,
            vulnerability_flag=vulnerability_flag,
            financial_exposure_inr=financial
        )
        reasoning = "Deterministic severity calculation."
        if self.llm_client is not None:
            prompt = f"""Explain this computed travel-disruption severity in two concise sentences for an operations agent.
Do not alter the score or label, and do not add facts. Score result: {severity}.
Inputs: impact={impact_score}, hours_to_departure={hours_to_departure}, financial_exposure={financial}, vulnerability={vulnerability_flag}."""
            try:
                reasoning = await self.llm_client.generate(prompt)
            except RuntimeError:
                pass
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        return AgentResult(
            agent=self.name,
            status="success",
            output=severity,
            confidence=1.0,
            duration_ms=duration_ms,
            reasoning=reasoning,
            evidence=[]
        )
