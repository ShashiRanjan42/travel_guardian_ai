import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Itinerary, ItineraryLeg, Incident, RecoveryPlan, AgentLog, Customer
from app.agents.graph import agent_graph

router = APIRouter(prefix="/api/simulate", tags=["simulate"])

SIMULATION_PRESETS = {
    "MONSOON_MUMBAI_BOM": {
        "title": "Torrential Monsoon Rain & Flooding at Mumbai BOM",
        "type": "WEATHER",
        "severity": "CRITICAL",
        "description": "Mumbai Airport (BOM) ground stop declared due to 120mm/hr rainfall and low runway friction.",
        "coords": [19.0896, 72.8656]
    },
    "SMOG_DELHI_IGI": {
        "title": "Dense Winter Smog & CAT III-B Shutdown at Delhi DEL",
        "type": "WEATHER",
        "severity": "HIGH",
        "description": "Delhi IGI Airport operates at 20% capacity under heavy smog. Flight departures delayed 2.5 hours.",
        "coords": [28.5562, 77.1000]
    },
    "VANDE_BHARAT_RAIL_BLOCK": {
        "title": "High-Speed Rail Corridor Block — Vande Bharat Line",
        "type": "TRAFFIC",
        "severity": "HIGH",
        "description": "Unscheduled signaling work halts Vande Bharat Express between Mumbai CSMT and Pune/Bengaluru.",
        "coords": [18.9400, 72.8353]
    },
    "CYCLONE_BAY_OF_BENGAL": {
        "title": "NASA EONET Cyclone Alert — Coastal Chennai Corridor",
        "type": "DISASTER",
        "severity": "CRITICAL",
        "description": "Cyclone warning issued for Tamil Nadu coast with high sea swells impacting airport & rail arrivals.",
        "coords": [12.9941, 80.1709]
    }
}

@router.post("")
async def trigger_simulation(payload: dict = Body(...), db: Session = Depends(get_db)):
    preset_key = payload.get("preset", "MONSOON_MUMBAI_BOM")
    itinerary_id = payload.get("itinerary_id", "itinerary-1")
    
    preset = SIMULATION_PRESETS.get(preset_key, SIMULATION_PRESETS["MONSOON_MUMBAI_BOM"])
    
    it = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
    if not it:
        it = db.query(Itinerary).first()
        if not it:
            raise HTTPException(status_code=404, detail="No active itinerary available for simulation.")
            
    cust = db.query(Customer).filter(Customer.id == it.customer_id).first()
    legs = db.query(ItineraryLeg).filter(ItineraryLeg.itinerary_id == it.id).order_by(ItineraryLeg.sequence_order).all()
    
    itinerary_data = {
        "id": it.id,
        "title": it.title,
        "customer": {
            "name": cust.name if cust else "Traveler",
            "tier": cust.tier if cust else "VIP"
        },
        "legs": [
            {
                "id": l.id,
                "title": l.title,
                "leg_type": l.leg_type,
                "origin": l.origin,
                "destination": l.destination,
                "origin_lat": l.origin_lat,
                "origin_lon": l.origin_lon,
                "dest_lat": l.dest_lat,
                "dest_lon": l.dest_lon,
            } for l in legs
        ]
    }
    
    trigger_event = {
        "leg_id": legs[0].id if legs else "leg-1",
        "title": preset["title"],
        "type": preset["type"],
        "severity": preset["severity"],
        "description": preset["description"],
        "coords": preset["coords"]
    }
    
    # Run the 7-agent graph workflow
    agent_state = await agent_graph.run(itinerary_data, trigger_event)
    
    # Update DB state and risk level
    it.status = "DISRUPTED"
    it.risk_score = 95 if preset["severity"] == "CRITICAL" else 80
    it.risk_level = preset["severity"]
    if legs:
        legs[0].status = "DELAYED"
        
    incident_id = f"INC-{int(datetime.utcnow().timestamp())}"
    new_inc = Incident(
        id=incident_id,
        itinerary_id=it.id,
        leg_id=legs[0].id if legs else None,
        title=preset["title"],
        type=preset["type"],
        severity=preset["severity"],
        status="RECOVERY_PROPOSED",
        description=preset["description"],
        impact_summary=f"Primary leg delayed. AI Guardian synthesized 3 recovery options.",
        lat=preset["coords"][0],
        lon=preset["coords"][1],
        detected_at=datetime.utcnow()
    )
    db.add(new_inc)
    
    # Save recovery plans
    for idx, opt in enumerate(agent_state.recovery_options):
        plan = RecoveryPlan(
            id=f"PLAN-{incident_id}-{idx+1}",
            incident_id=incident_id,
            option_code=opt["option_code"],
            title=opt["title"],
            summary=opt["summary"],
            cost_delta=opt["cost_delta"],
            eta_delta_minutes=opt["eta_delta_minutes"],
            confidence_score=opt["confidence_score"],
            reasoning=opt["reasoning"],
            tradeoffs=opt.get("tradeoffs", ""),
            actions_json=json.dumps(opt.get("actions", [])),
            status="PROPOSED"
        )
        db.add(plan)
        
    for log in agent_state.logs:
        db_log = AgentLog(
            incident_id=incident_id,
            agent_name=log["agent_name"],
            status=log["status"],
            action=log["action"],
            details=log["details"],
            timestamp=datetime.utcnow()
        )
        db.add(db_log)
        
    db.commit()
    
    return {
        "status": "SUCCESS",
        "incident_id": incident_id,
        "preset_applied": preset["title"],
        "disruptions_count": len(agent_state.disruptions),
        "recovery_options_count": len(agent_state.recovery_options),
        "agent_logs_count": len(agent_state.logs),
        "graph_state": {
            "telemetry": agent_state.telemetry,
            "disruptions": agent_state.disruptions,
            "impacts": agent_state.impacts,
            "recovery_options": agent_state.recovery_options,
            "communications": agent_state.communications,
            "ops_analytics": agent_state.ops_analytics,
            "logs": agent_state.logs
        }
    }
