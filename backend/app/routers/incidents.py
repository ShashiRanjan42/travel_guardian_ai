import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Incident, RecoveryPlan, Itinerary, ItineraryLeg, AgentLog

router = APIRouter(prefix="/api/incidents", tags=["incidents"])

@router.get("")
def list_all_incidents(db: Session = Depends(get_db)):
    incidents = db.query(Incident).order_by(Incident.detected_at.desc()).all()
    results = []
    for inc in incidents:
        it = db.query(Itinerary).filter(Itinerary.id == inc.itinerary_id).first()
        plans = db.query(RecoveryPlan).filter(RecoveryPlan.incident_id == inc.id).all()
        results.append({
            "id": inc.id,
            "itinerary_id": inc.itinerary_id,
            "itinerary_title": it.title if it else "Trip",
            "customer_name": it.customer.name if (it and it.customer) else "Traveler",
            "customer_email": it.customer.email if (it and it.customer) else "",
            "title": inc.title,
            "type": inc.type,
            "severity": inc.severity,
            "status": inc.status,
            "description": inc.description,
            "impact_summary": inc.impact_summary,
            "lat": inc.lat,
            "lon": inc.lon,
            "detected_at": inc.detected_at.isoformat(),
            "recovery_plans_count": len(plans)
        })
    return results

@router.post("/{incident_id}/approve_plan")
def approve_recovery_plan(incident_id: str, payload: dict = Body(...), db: Session = Depends(get_db)):
    plan_id = payload.get("plan_id")
    if not plan_id:
        raise HTTPException(status_code=400, detail="plan_id required")
    
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    selected_plan = db.query(RecoveryPlan).filter(RecoveryPlan.id == plan_id).first()
    if not selected_plan:
        raise HTTPException(status_code=404, detail="Recovery plan not found")

    all_plans = db.query(RecoveryPlan).filter(RecoveryPlan.incident_id == incident_id).all()
    for p in all_plans:
        if p.id == plan_id:
            p.status = "APPROVED"
        else:
            p.status = "REJECTED"

    inc.status = "RECOVERED"
    
    it = db.query(Itinerary).filter(Itinerary.id == inc.itinerary_id).first()
    if it:
        it.status = "RECOVERED"
        it.risk_score = 10
        it.risk_level = "LOW"
        disrupted_leg = db.query(ItineraryLeg).filter(ItineraryLeg.itinerary_id == it.id, ItineraryLeg.status == "DELAYED").first()
        if not disrupted_leg:
            disrupted_leg = db.query(ItineraryLeg).filter(ItineraryLeg.itinerary_id == it.id).first()
        
        if disrupted_leg:
            disrupted_leg.status = "REBOOKED"
            disrupted_leg.title = f"[REBOOKED] {selected_plan.title}"
            disrupted_leg.operator = "Partner Rebook"
            
    new_log = AgentLog(
        incident_id=inc.id,
        agent_name="Booking & Coordination Agent",
        status="SUCCESS",
        action="PLAN_APPROVED_AND_EXECUTED",
        details=f"Customer approved Plan '{selected_plan.title}'. Carrier seats confirmed, ticketing re-issued.",
        timestamp=datetime.utcnow()
    )
    db.add(new_log)
    db.commit()
    
    return {
        "status": "SUCCESS",
        "message": f"Plan '{selected_plan.title}' approved and executed successfully!",
        "incident_status": inc.status,
        "itinerary_status": it.status if it else "RECOVERED"
    }
