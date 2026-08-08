from fastapi import APIRouter, Depends, Body
from app.services.llm_booking_agent import llm_booking_agent

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("/graph_nodes")
def get_agent_graph_metadata():
    """Metadata for frontend visualization of the 7 LangGraph AI agents."""
    return {
        "nodes": [
            {"id": "SUPERVISOR", "name": "Supervisor Agent", "type": "ORCHESTRATOR", "role": "State machine routing & final verification"},
            {"id": "JOURNEY_MONITORING", "name": "Journey Monitoring Agent", "type": "WORKER", "role": "Continuously polls Open-Meteo, Nominatim, OSRM, NASA EONET"},
            {"id": "DISRUPTION_DETECTION", "name": "Disruption Detection Agent", "type": "WORKER", "role": "Anomaly detection on weather, delays, ground stops, strikes"},
            {"id": "IMPACT_ANALYSIS", "name": "Impact Analysis Agent", "type": "WORKER", "role": "Calculates downstream layover and hotel cascading impacts"},
            {"id": "RECOVERY_PLANNING", "name": "Recovery Planning Agent", "type": "WORKER", "role": "Synthesizes multi-modal options with cost/ETA & RAG policies"},
            {"id": "BOOKING_COORDINATION", "name": "Booking & Coordination Agent", "type": "WORKER", "role": "Simulates carrier holds, electronic ticketing, and rebooking"},
            {"id": "CUSTOMER_COMMUNICATION", "name": "Customer Communication Agent", "type": "WORKER", "role": "Drafts SMS, Push notifications, and interactive chat responses"},
            {"id": "OPERATIONS_DASHBOARD", "name": "Operations Dashboard Agent", "type": "WORKER", "role": "Pushes telemetry metrics and updates fleet risk matrix"}
        ],
        "edges": [
            {"from": "SUPERVISOR", "to": "JOURNEY_MONITORING"},
            {"from": "JOURNEY_MONITORING", "to": "DISRUPTION_DETECTION"},
            {"from": "DISRUPTION_DETECTION", "to": "IMPACT_ANALYSIS"},
            {"from": "IMPACT_ANALYSIS", "to": "RECOVERY_PLANNING"},
            {"from": "RECOVERY_PLANNING", "to": "CUSTOMER_COMMUNICATION"},
            {"from": "CUSTOMER_COMMUNICATION", "to": "BOOKING_COORDINATION"},
            {"from": "BOOKING_COORDINATION", "to": "OPERATIONS_DASHBOARD"},
            {"from": "OPERATIONS_DASHBOARD", "to": "SUPERVISOR"}
        ]
    }

from app.integrations.llm.openai_responses import OpenAIResponsesClient

@router.post("/chat_book")
async def chat_booking_turn(payload: dict = Body(...)):
    session_id = payload.get("session_id", "default_session")
    message = payload.get("message", "")
    user_name = payload.get("user_name", "Traveler")

    result = await llm_booking_agent.process_message(session_id, message, user_name)
    return result

@router.post("/chat_ops")
async def chat_ops_turn(payload: dict = Body(...)):
    message = payload.get("message", "")
    
    llm = OpenAIResponsesClient()
    prompt = f"""You are the Operations AI Copilot for Wayfare Travel Guardian.
The operations manager just asked you this: "{message}"

Respond concisely in 1-3 sentences. If they ask about status, confirm the 10-Agent Swarm is online and monitoring telemetry. If they ask about an incident, provide a quick analytical summary.
Do not use markdown wrappers, just return plain text."""
    
    try:
        reply = await llm.generate(prompt)
        return {"reply": reply}
    except Exception as e:
        return {"reply": "Network error connecting to Operations Copilot."}
