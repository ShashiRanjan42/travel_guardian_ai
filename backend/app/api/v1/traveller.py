from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.data.session import get_db
from app.data.models import ImpactAssessment, ReplanOption, DisruptionEvent, Booking
from sqlalchemy import select
from app.api.v1.auth import get_current_user

router = APIRouter()

@router.get("/traveller/notifications")
async def get_notifications(db = Depends(get_db), user: dict = Depends(get_current_user)):
    if user["role"] != "traveller" or not user.get("traveller_id"):
        raise HTTPException(status_code=403, detail="Traveller access required")
        
    # Mocking for demo - fetch dispatched assessments
    result = await db.execute(select(ImpactAssessment, DisruptionEvent)
                              .join(DisruptionEvent, ImpactAssessment.event_id == DisruptionEvent.id)
                              .where(ImpactAssessment.status == 'DISPATCHED'))
    rows = result.all()
    
    data = []
    for assess, event in rows:
        data.append({
            "id": str(assess.id),
            "headline": event.headline,
            "message": "Your itinerary requires a change due to a disruption. We have found alternative options.",
            "requires_action": True
        })
    return {"data": data}

@router.get("/traveller/decisions/{alert_id}")
async def get_decision(alert_id: str, db = Depends(get_db), user: dict = Depends(get_current_user)):
    if user["role"] != "traveller" or not user.get("traveller_id"):
        raise HTTPException(status_code=403, detail="Traveller access required")
        
    result = await db.execute(select(ImpactAssessment, DisruptionEvent)
                              .join(DisruptionEvent, ImpactAssessment.event_id == DisruptionEvent.id)
                              .where(ImpactAssessment.id == alert_id))
    row = result.first()
    if not row:
        raise HTTPException(status_code=404)
        
    assess, event = row
    
    # fetch APPROVED options ONLY (G-12 Data Minimisation)
    opt_res = await db.execute(select(ReplanOption)
                               .where(ReplanOption.assessment_id == assess.id)
                               .where(ReplanOption.status == 'APPROVED')
                               .order_by(ReplanOption.rank))
    options = opt_res.scalars().all()
    
    opts_data = []
    for opt in options:
        opts_data.append({
            "id": str(opt.id),
            "label": opt.label,
            "cost_delta_inr": opt.cost_delta_inr,
            "time_delta_minutes": opt.time_delta_minutes,
            "tradeoffs": opt.tradeoffs,
            "status": opt.status,
            "summary": opt.summary,
            "changed_legs": []
            # Deliberately omitting risk_score, confidence, evidence, assumptions, etc.
        })
        
    return {
        "data": {
            "alert_id": str(assess.id),
            "headline": event.headline,
            "impact_summary": assess.impact_summary,
            "options": opts_data
        }
    }

@router.get("/traveller/alerts/{alert_id}")
async def get_traveller_alert(alert_id: str, db = Depends(get_db), user: dict = Depends(get_current_user)):
    """Compatibility endpoint used by the traveller trip view."""
    return await get_decision(alert_id, db, user)

@router.post("/traveller/bookings/{id}/alerts/{alert_id}/select")
async def select_option(id: str, alert_id: str, payload: dict, db = Depends(get_db), user: dict = Depends(get_current_user)):
    if user["role"] != "traveller" or not user.get("traveller_id"):
        raise HTTPException(status_code=403, detail="Traveller access required")
        
    option_id = payload.get("option_id")
    
    # Authorize against booking
    result = await db.execute(select(Booking).where(Booking.id == id))
    booking = result.scalar_one_or_none()
    if not booking or booking.traveller_id != user["traveller_id"]:
        raise HTTPException(status_code=403, detail="Forbidden: Booking does not belong to this traveller")
        
    result = await db.execute(select(ImpactAssessment).where(ImpactAssessment.id == alert_id).where(ImpactAssessment.booking_id == id))
    assess = result.scalar_one_or_none()
    if assess:
        assess.status = "RESOLVED"
        await db.commit()
        
    return {"data": {"status": "success"}}

@router.get("/traveller/bookings/{id}")
async def get_booking(id: str, db = Depends(get_db), user: dict = Depends(get_current_user)):
    if user["role"] != "traveller" or not user.get("traveller_id"):
        raise HTTPException(status_code=403, detail="Traveller access required")
        
    result = await db.execute(select(Booking).where(Booking.id == id))
    booking = result.scalar_one_or_none()
    if not booking or booking.traveller_id != user["traveller_id"]:
        raise HTTPException(status_code=403, detail="Forbidden: Booking does not belong to this traveller")
        
    return {
        "data": {
            "id": str(booking.id),
            "pnr": booking.pnr,
            "origin": booking.origin,
            "destination": booking.destination,
            "start_date": booking.start_date.isoformat() if hasattr(booking.start_date, 'isoformat') else str(booking.start_date),
            "end_date": booking.end_date.isoformat() if hasattr(booking.end_date, 'isoformat') else str(booking.end_date),
            "total_value_inr": booking.total_value_inr,
            "status": booking.status
        }
    }

@router.get("/traveller/bookings/{id}/diff")
async def get_booking_diff(id: str, db = Depends(get_db), user: dict = Depends(get_current_user)):
    if user["role"] != "traveller" or not user.get("traveller_id"):
        raise HTTPException(status_code=403, detail="Traveller access required")
        
    # Mock diff data for now
    return {
        "data": {
            "booking_id": id,
            "changes": [
                {
                    "seq": 2,
                    "change_type": "MODIFIED",
                    "before": "Check-in at Riverside Homestay 12:00 PM",
                    "after": "Check-in at Riverside Homestay 04:00 PM"
                }
            ]
        }
    }
