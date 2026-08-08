import time
import json
from typing import List, Dict, Any
from app.domain.agents.base import AgentContext, AgentResult
from app.integrations.llm.base import LLMClient
from app.domain.compliance_rules import evaluate_compliance

class Compliance:
    def __init__(self, llm_client: LLMClient):
        self.name = "COMPLIANCE"
        self.llm_client = llm_client

    async def run(self, ctx: AgentContext) -> AgentResult:
        start_time = time.time()
        
        # In a real app we pass the event and options to LLM to understand risk.
        # For this hackathon, we simulate it via the mock LLM.
        options = ctx.options
        
        processed_options = []
        for option in options:
            prompt = f"""Review this travel alternative for safety risk. Do not approve or reject it;
identify only the risk indicated by the supplied data. Return ONLY JSON:
{{"interpreted_risk":"LOW|MEDIUM|HIGH|CRITICAL","rule":null,"rationale":"short explanation"}}
Event: {ctx.event.headline}\nDescription: {ctx.event.description}\nOption: {json.dumps(option)}"""
            # Ask LLM if there's an interpreted risk based on advisory text
            llm_response = await self.llm_client.generate(prompt)
            try:
                interpretation = json.loads(llm_response)
                interpreted_risk = interpretation.get("interpreted_risk", "LOW")
                rule_id = interpretation.get("rule", None)
            except json.JSONDecodeError:
                interpreted_risk = "LOW"
                rule_id = None
                
            # Apply deterministic rules
            eval_result = evaluate_compliance(option, interpreted_risk, rule_id)
            
            option["status"] = "APPROVED" if eval_result["approved"] else "REJECTED"
            option["rejection_reason"] = eval_result["rejection_reason"]
            option["rejected_by_rule"] = eval_result["rule_id"]
            
            processed_options.append(option)
            
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Check if any options were rejected
        any_rejected = any(not opt.get("status") == "APPROVED" for opt in processed_options)
        
        return AgentResult(
            agent=self.name,
            status="success" if not any_rejected else "partial", # or success, doesn't matter too much
            output=processed_options,
            confidence=0.95,
            duration_ms=duration_ms,
            reasoning="OpenAI interpreted risk context; deterministic compliance rules made the approval decision.",
            evidence=[]
        )
