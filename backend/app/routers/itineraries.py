import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Customer, Itinerary, ItineraryLeg, Incident, RecoveryPlan, AgentLog

router = APIRouter(prefix="/api/itineraries", tags=["itineraries"])

@router.get("")
def list_itineraries(db: Session = Depends(get_db)):
    """
    Returns ALL customer itineraries sorted by High Risk first (risk_score descending).
    """
    itineraries = db.query(Itinerary).order_by(Itinerary.risk_score.desc()).all()
    results = []
    for it in itineraries:
        legs = db.query(ItineraryLeg).filter(ItineraryLeg.itinerary_id == it.id).order_by(ItineraryLeg.sequence_order).all()
        incidents = db.query(Incident).filter(Incident.itinerary_id == it.id).all()
        cust = db.query(Customer).filter(Customer.id == it.customer_id).first()
        
        active_inc = next((inc for inc in incidents if inc.status in ["OPEN", "RECOVERY_PROPOSED"]), None)
        risk_score = it.risk_score
        risk_level = it.risk_level
        if active_inc:
            if active_inc.severity == "CRITICAL":
                risk_score = max(risk_score, 95)
                risk_level = "CRITICAL"
            elif active_inc.severity == "HIGH":
                risk_score = max(risk_score, 80)
                risk_level = "HIGH"
            elif active_inc.severity == "MEDIUM":
                risk_score = max(risk_score, 55)
                risk_level = "ELEVATED"

        results.append({
            "id": it.id,
            "title": it.title,
            "status": it.status,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "start_date": it.start_date.isoformat(),
            "end_date": it.end_date.isoformat(),
            "customer": {
                "id": cust.id if cust else "",
                "name": cust.name if cust else "Unknown Traveler",
                "email": cust.email if cust else "",
                "tier": cust.tier if cust else "VIP",
                "home_city": cust.home_city if cust else "India"
            },
            "leg_count": len(legs),
            "incident_count": len(incidents),
            "active_incident": {
                "id": active_inc.id,
                "title": active_inc.title,
                "severity": active_inc.severity,
                "type": active_inc.type,
                "description": active_inc.description
            } if active_inc else None,
            "legs": [
                {
                    "id": l.id,
                    "leg_type": l.leg_type,
                    "sequence_order": l.sequence_order,
                    "title": l.title,
                    "operator": l.operator,
                    "code": l.code,
                    "origin": l.origin,
                    "destination": l.destination,
                    "origin_lat": l.origin_lat,
                    "origin_lon": l.origin_lon,
                    "dest_lat": l.dest_lat,
                    "dest_lon": l.dest_lon,
                    "departure_time": l.departure_time.isoformat(),
                    "arrival_time": l.arrival_time.isoformat(),
                    "status": l.status
                } for l in legs
            ]
        })
        
    results.sort(key=lambda x: x["risk_score"], reverse=True)
    return results

@router.post("/create")
def create_new_booking(payload: dict = Body(...), db: Session = Depends(get_db)):
    booking_type = payload.get("booking_type", "FLIGHT").upper()
    customer_id = payload.get("customer_id", "cust-1")
    origin = payload.get("origin", "Delhi (DEL)")
    destination = payload.get("destination", "Mumbai (BOM)")
    operator = payload.get("operator", "IndiGo Airlines")
    travel_date_str = payload.get("travel_date", datetime.utcnow().strftime("%Y-%m-%d"))

    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        cust = db.query(Customer).first()
        customer_id = cust.id if cust else "cust-1"

    try:
        travel_date = datetime.strptime(travel_date_str, "%Y-%m-%d")
    except Exception:
        travel_date = datetime.utcnow() + timedelta(days=2)

    it_id = f"itinerary-custom-{int(datetime.utcnow().timestamp())}"
    title = f"{cust.name if cust else 'Traveler'} — {booking_type.title()} ({origin} to {destination})"

    new_it = Itinerary(
        id=it_id,
        customer_id=customer_id,
        title=title,
        status="OK",
        risk_score=15,
        risk_level="LOW",
        start_date=travel_date,
        end_date=travel_date + timedelta(days=3)
    )
    db.add(new_it)
    db.commit()

    # Lat/Lon mappings for Indian hubs
    coords_map = {
        "Delhi": (28.5562, 77.1000),
        "Mumbai": (19.0896, 72.8656),
        "Bengaluru": (13.1986, 77.7066),
        "Hyderabad": (17.2403, 78.4294),
        "Chennai": (12.9941, 80.1709),
        "Kolkata": (22.6547, 88.4467),
        "Jaipur": (26.8242, 75.8122),
        "Goa": (15.3808, 73.8314)
    }

    orig_coords = coords_map.get("Delhi", (28.5562, 77.1000))
    for k in coords_map:
        if k.lower() in origin.lower():
            orig_coords = coords_map[k]

    dest_coords = coords_map.get("Mumbai", (19.0896, 72.8656))
    for k in coords_map:
        if k.lower() in destination.lower():
            dest_coords = coords_map[k]

    leg1 = ItineraryLeg(
        id=f"leg-c-{int(datetime.utcnow().timestamp())}-1",
        itinerary_id=it_id,
        sequence_order=1,
        leg_type=booking_type,
        title=f"{operator} • {origin} to {destination}",
        operator=operator,
        code=f"BOOK-{int(datetime.utcnow().timestamp())%10000}",
        origin=origin,
        destination=destination,
        origin_lat=orig_coords[0],
        origin_lon=orig_coords[1],
        dest_lat=dest_coords[0],
        dest_lon=dest_coords[1],
        departure_time=travel_date + timedelta(hours=10),
        arrival_time=travel_date + timedelta(hours=13),
        status="SCHEDULED"
    )
    db.add(leg1)
    db.commit()

    return {
        "status": "SUCCESS",
        "message": f"Successfully booked protected {booking_type.title()} from {origin} to {destination}!",
        "itinerary_id": it_id
    }

@router.get("/{itinerary_id}")
def get_itinerary_detail(itinerary_id: str, db: Session = Depends(get_db)):
    it = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
    if not it:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
    legs = db.query(ItineraryLeg).filter(ItineraryLeg.itinerary_id == it.id).order_by(ItineraryLeg.sequence_order).all()
    incidents = db.query(Incident).filter(Incident.itinerary_id == it.id).all()
    cust = db.query(Customer).filter(Customer.id == it.customer_id).first()
    
    incidents_data = []
    for inc in incidents:
        plans = db.query(RecoveryPlan).filter(RecoveryPlan.incident_id == inc.id).all()
        logs = db.query(AgentLog).filter(AgentLog.incident_id == inc.id).order_by(AgentLog.timestamp.desc()).all()
        incidents_data.append({
            "id": inc.id,
            "title": inc.title,
            "type": inc.type,
            "severity": inc.severity,
            "status": inc.status,
            "description": inc.description,
            "impact_summary": inc.impact_summary,
            "lat": inc.lat,
            "lon": inc.lon,
            "detected_at": inc.detected_at.isoformat(),
            "recovery_plans": [
                {
                    "id": p.id,
                    "option_code": p.option_code,
                    "title": p.title,
                    "summary": p.summary,
                    "cost_delta": p.cost_delta,
                    "eta_delta_minutes": p.eta_delta_minutes,
                    "confidence_score": p.confidence_score,
                    "reasoning": p.reasoning,
                    "tradeoffs": p.tradeoffs,
                    "status": p.status,
                    "actions": json.loads(p.actions_json or "[]")
                } for p in plans
            ],
            "agent_logs": [
                {
                    "id": lg.id,
                    "agent_name": lg.agent_name,
                    "status": lg.status,
                    "action": lg.action,
                    "details": lg.details,
                    "timestamp": lg.timestamp.isoformat()
                } for lg in logs
            ]
        })

    return {
        "id": it.id,
        "title": it.title,
        "status": it.status,
        "risk_score": it.risk_score,
        "risk_level": it.risk_level,
        "start_date": it.start_date.isoformat(),
        "end_date": it.end_date.isoformat(),
        "customer": {
            "id": cust.id if cust else "",
            "name": cust.name if cust else "Unknown",
            "email": cust.email if cust else "",
            "phone": cust.phone if cust else "",
            "tier": cust.tier if cust else "VIP",
            "home_city": cust.home_city if cust else "India"
        },
        "legs": [
            {
                "id": l.id,
                "leg_type": l.leg_type,
                "sequence_order": l.sequence_order,
                "title": l.title,
                "operator": l.operator,
                "code": l.code,
                "origin": l.origin,
                "destination": l.destination,
                "origin_lat": l.origin_lat,
                "origin_lon": l.origin_lon,
                "dest_lat": l.dest_lat,
                "dest_lon": l.dest_lon,
                "departure_time": l.departure_time.isoformat(),
                "arrival_time": l.arrival_time.isoformat(),
                "status": l.status,
                "details": json.loads(l.details_json or "{}")
            } for l in legs
        ],
        "incidents": incidents_data
    }
