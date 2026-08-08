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
        
        # We need the ChatOpenAI client
        if not hasattr(self.llm_client, "get_client"):
            raise RuntimeError("Replanner requires an LLMClient with get_client() returning a ChatOpenAI instance.")
            
        chat_model = self.llm_client.get_client()
        
        from langgraph.prebuilt import create_react_agent
        from langchain_core.messages import SystemMessage
        from app.domain.agents.tools import search_flights, search_hotels, search_trains, check_weather
        
        tools = [search_flights, search_hotels, search_trains, check_weather]
        
        system_message = f"""You are a highly capable travel replanning specialist.
You must use the provided tools to search for live flights, hotels, or trains to help a disrupted traveller.
You must absolutely prioritize the Traveller's constraints (e.g. VIP status, vulnerability flags, preferences).

Event: {ctx.event.headline}
Event details: {ctx.event.description}
Traveller profile: {json.dumps(ctx.traveller_profile) if ctx.traveller_profile else "None provided"}

Your goal is to suggest up to three practical options.
You must ONLY output valid JSON strictly adhering to this format:
{{"options":[{{"rank":1,"label":"...","summary":"...","cost_delta_inr":0,"time_delta_minutes":0,"risk_score":0.0,"confidence":0.0,"evidence":[{{"source":"Tool output or logic","claim":"..."}}],"assumptions":["..."],"tradeoffs":"..."}}]}}
Do NOT output any markdown blocks or extra text outside the JSON."""
        
        agent = create_react_agent(chat_model, tools, prompt=system_message)
        
        try:
            result = await agent.ainvoke({"messages": [("user", "Plan the alternatives now using tools if needed.")]})
            
            output_text = result["messages"][-1].content
            
            # Strip markdown block if present
            if output_text.startswith("```json"):
                output_text = output_text[7:]
            if output_text.endswith("```"):
                output_text = output_text[:-3]
                
            data = json.loads(output_text.strip())
            options = data.get("options", [])
        except Exception as e:
            print(f"Replanner Agent Execution Error: {e}")
            options = []
            
        # Groundedness Enforcement (G-5)
        valid_options = []
        for opt in options:
            if not opt.get("evidence"):
                continue
            valid_options.append(opt)
            
        duration_ms = int((time.time() - start_time) * 1000)
        
        return AgentResult(
            agent=self.name,
            status="success" if valid_options else "failed",
            output=valid_options,
            confidence=0.9,
            duration_ms=duration_ms,
            reasoning="Replanner Agent used tools to find contextual options aligned with user profile.",
            evidence=[]
        )
