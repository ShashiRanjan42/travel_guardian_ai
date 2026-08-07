from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import AgentLog
from app.services.llm_booking_agent import llm_booking_agent

router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.get("/logs")
def get_all_agent_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(AgentLog).order_by(AgentLog.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "incident_id": l.incident_id,
            "agent_name": l.agent_name,
            "status": l.status,
            "action": l.action,
            "details": l.details,
            "timestamp": l.timestamp.isoformat()
        } for l in logs
    ]

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

@router.post("/chat_book")
def chat_booking_turn(payload: dict = Body(...)):
    session_id = payload.get("session_id", "default_session")
    message = payload.get("message", "")
    user_name = payload.get("user_name", "Traveler")

    result = llm_booking_agent.process_message(session_id, message, user_name)
    return result
