import asyncio
import os
import sys

# Add backend2 to sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend2')))

from app.integrations.llm.openai_responses import OpenAIResponsesClient
from app.domain.agents.replanner import Replanner
from app.domain.agents.base import AgentContext
from app.data.models import DisruptionEvent, ImpactAssessment
import uuid

async def main():
    print("Initializing LLM Client...")
    llm_client = OpenAIResponsesClient()
    
    print("Initializing Replanner Agent...")
    replanner = Replanner(llm_client)
    
    event = DisruptionEvent(
        id=uuid.uuid4(),
        type="FLIGHT_CANCELLED",
        headline="Delhi to Mumbai Flight Blockage",
        description="Major runway blockage at DEL preventing departure to Mumbai. Flight cancelled.",
        affected_modes=["FLIGHT"]
    )
    
    assessment = ImpactAssessment(
        id=uuid.uuid4(),
        booking_id=uuid.uuid4(),
        itinerary_id=uuid.uuid4(),
        event_id=event.id
    )
    
    ctx = AgentContext(
        run_id=str(uuid.uuid4()),
        event=event,
        assessment=assessment,
        options=[],
        itinerary=None,
        traveller_profile={
            "is_solo": True,
            "vulnerability_flag": False,
            "preferences": {
                "preferred_carrier": "Air India",
                "hotel_star_rating": 5,
                "max_budget_inr": 20000,
                "strict_requirements": "Never route through Chandigarh. Only direct alternatives to Mumbai."
            }
        },
        prior_results={}
    )
    
    print("\nRunning Replanner Agent...")
    print("This will call the live TCS GenAI Lab API and use Langchain Tools (search_flights, search_trains, etc.)")
    print("-" * 50)
    
    result = await replanner.run(ctx)
    
    print(f"\nStatus: {result.status}")
    print(f"Duration: {result.duration_ms} ms")
    print(f"Reasoning: {result.reasoning}")
    print("\nGenerated Options:")
    
    import json
    print(json.dumps(result.output, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
