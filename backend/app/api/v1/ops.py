from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.data.session import get_db
from app.data.models import Booking, ImpactAssessment, ReplanOption, AgentTrace, DisruptionEvent
from sqlalchemy import select, func

router = APIRouter()

@router.get("/ops/dashboard/summary")
async def get_summary(db = Depends(get_db)):
    result = await db.execute(select(func.count(Booking.id)).where(Booking.status == 'active'))
    active_bookings = result.scalar()
    
    result = await db.execute(select(func.count(ImpactAssessment.id)).where(ImpactAssessment.status != 'RESOLVED'))
    open_alerts = result.scalar()
    
    return {
        "data": {
            "active_bookings": active_bookings,
            "departing_72h": 12, # mock for demo
            "open_alerts": open_alerts,
            "avg_resolution_time_sec": 94,
            "time_saved_pct": 96.5
        }
    }

@router.get("/ops/bookings")
async def get_bookings(db = Depends(get_db)):
    from app.data.models import Booking, Traveller
    result = await db.execute(select(Booking, Traveller).join(Traveller, Booking.traveller_id == Traveller.id).limit(50))
    rows = result.all()
    
    data = []
    for b, t in rows:
        data.append({
            "id": str(b.id),
            "pnr": b.pnr,
            "origin": b.origin,
            "destination": b.destination,
            "start_date": b.start_date.isoformat() if hasattr(b.start_date, 'isoformat') else str(b.start_date),
            "end_date": b.end_date.isoformat() if hasattr(b.end_date, 'isoformat') else str(b.end_date),
            "total_value_inr": b.total_value_inr,
            "non_refundable_value_inr": b.non_refundable_value_inr,
            "status": b.status,
            "traveller": {
                "id": str(t.id),
                "full_name": t.full_name,
                "email": t.email,
                "phone": t.phone,
                "is_solo": t.is_solo,
                "vulnerability_flag": t.vulnerability_flag
            }
        })
    return {
        "data": {
            "items": data,
            "total": len(data),
            "page": 1,
            "size": 20
        }
    }

@router.get("/ops/bookings/{id}")
async def get_booking(id: str, db = Depends(get_db)):
    result = await db.execute(select(Booking, Traveller).join(Traveller, Booking.traveller_id == Traveller.id).where(Booking.id == id))
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Booking not found")
    b, t = row
    return {"data": {
        "id": str(b.id), "pnr": b.pnr, "origin": b.origin, "destination": b.destination,
        "start_date": b.start_date.isoformat(), "end_date": b.end_date.isoformat(),
        "total_value_inr": b.total_value_inr, "non_refundable_value_inr": b.non_refundable_value_inr,
        "status": b.status,
        "traveller": {"id": str(t.id), "full_name": t.full_name, "email": t.email, "phone": t.phone,
                      "is_solo": t.is_solo, "vulnerability_flag": t.vulnerability_flag}
    }}

@router.get("/ops/alerts")
async def get_alerts(db = Depends(get_db)):
    from app.data.models import Booking, Traveller
    result = await db.execute(select(ImpactAssessment, DisruptionEvent, Booking, Traveller)
                              .join(DisruptionEvent, ImpactAssessment.event_id == DisruptionEvent.id)
                              .join(Booking, ImpactAssessment.booking_id == Booking.id)
                              .join(Traveller, Booking.traveller_id == Traveller.id)
                              .order_by(ImpactAssessment.severity_score.desc()))
    rows = result.all()
    
    data = []
    for assess, event, booking, traveller in rows:
        data.append({
            "id": str(assess.id),
            "booking_id": str(booking.id),
            "booking_pnr": booking.pnr,
            "traveller_name": traveller.full_name,
            "destination": booking.destination,
            "headline": event.headline,
            "disruption_type": event.type,
            "severity": assess.severity,
            "severity_score": assess.severity_score,
            "status": assess.status,
            "hours_to_departure": assess.hours_to_departure,
            "affected_leg_count": len(assess.affected_leg_ids) if assess.affected_leg_ids else 0,
            "cascade_leg_count": len(assess.cascade_leg_ids) if assess.cascade_leg_ids else 0
        })
    return {
        "data": {
            "items": data,
            "total": len(data),
            "page": 1,
            "size": 20
        }
    }

@router.get("/ops/alerts/{id}")
async def get_alert_detail(id: str, db = Depends(get_db)):
    result = await db.execute(select(ImpactAssessment, DisruptionEvent)
                              .join(DisruptionEvent, ImpactAssessment.event_id == DisruptionEvent.id)
                              .where(ImpactAssessment.id == id))
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    assess, event = row
    
    # fetch options
    opt_res = await db.execute(select(ReplanOption).where(ReplanOption.assessment_id == assess.id))
    options = opt_res.scalars().all()
    
    opts_data = []
    for opt in options:
        opts_data.append({
            "id": str(opt.id),
            "label": opt.label,
            "summary": opt.summary,
            "cost_delta_inr": opt.cost_delta_inr,
            "time_delta_minutes": opt.time_delta_minutes,
            "risk_score": opt.risk_score,
            "confidence": opt.confidence,
            "status": opt.status,
            "evidence": opt.evidence,
            "assumptions": opt.assumptions,
            "tradeoffs": opt.tradeoffs,
            "rejection_reason": opt.rejection_reason,
            "rejected_by_rule": opt.rejected_by_rule
            ,"rank": opt.rank,
            "changed_legs": [],
            "expires_at": opt.expires_at.isoformat() if opt.expires_at else None
        })
        
    return {
        "data": {
            "id": str(assess.id),
            "status": assess.status,
            "headline": event.headline,
            "severity": assess.severity,
            "score": assess.severity_score,
            "severity_breakdown": assess.severity_breakdown,
            "impact_summary": assess.impact_summary,
            "affected_legs": assess.affected_leg_ids,
            "cascade_legs": assess.cascade_leg_ids,
            "options": opts_data
        }
    }

@router.get("/ops/alerts/{id}/trace")
async def get_alert_trace(id: str, db = Depends(get_db)):
    result = await db.execute(select(AgentTrace).where(AgentTrace.assessment_id == id).order_by(AgentTrace.seq))
    traces = result.scalars().all()
    
    data = []
    for t in traces:
        data.append({
            "agent": t.agent,
            "status": t.status,
            "duration_ms": t.duration_ms,
            "reasoning": t.reasoning
        })
    return {"data": data}

@router.post("/ops/alerts/{id}/dispatch")
async def dispatch_alert(id: str, payload: dict, db = Depends(get_db)):
    result = await db.execute(select(ImpactAssessment).where(ImpactAssessment.id == id))
    assess = result.scalar_one_or_none()
    if not assess:
        raise HTTPException(status_code=404)
        
    # Validation: Enforce at least 2 approved options for dispatch
    opt_res = await db.execute(select(ReplanOption).where(ReplanOption.assessment_id == id, ReplanOption.status == 'APPROVED'))
    approved_options = opt_res.scalars().all()
    if len(approved_options) < 2:
        raise HTTPException(status_code=409, detail="At least 2 approved options are required for dispatch")
        
    assess.status = "DISPATCHED"
    await db.commit()
    
    return {"data": {"status": "success"}}

@router.post("/ops/alerts/{alert_id}/options/{option_id}/approve")
async def approve_option(alert_id: str, option_id: str, payload: dict, db = Depends(get_db)):
    result = await db.execute(select(ReplanOption).where(ReplanOption.id == option_id, ReplanOption.assessment_id == alert_id))
    option = result.scalar_one_or_none()
    if not option:
        raise HTTPException(status_code=404, detail="Option not found")
        
    option.status = "APPROVED"
    option.approved_by = "usr_ops1" # mock user
    await db.commit()
    return {"data": {"status": "success"}}

@router.post("/ops/alerts/{alert_id}/options/{option_id}/reject")
async def reject_option(alert_id: str, option_id: str, payload: dict, db = Depends(get_db)):
    result = await db.execute(select(ReplanOption).where(ReplanOption.id == option_id, ReplanOption.assessment_id == alert_id))
    option = result.scalar_one_or_none()
    if not option:
        raise HTTPException(status_code=404, detail="Option not found")
        
    option.status = "REJECTED"
    option.rejection_reason = payload.get("reason", "Manual rejection")
    await db.commit()
    return {"data": {"status": "success"}}

@router.post("/ops/alerts/{alert_id}/options/{option_id}/override-approve")
async def override_approve_option(alert_id: str, option_id: str, payload: dict, db = Depends(get_db)):
    result = await db.execute(select(ReplanOption).where(ReplanOption.id == option_id, ReplanOption.assessment_id == alert_id))
    option = result.scalar_one_or_none()
    if not option:
        raise HTTPException(status_code=404, detail="Option not found")
        
    option.status = "OVERRIDDEN"
    option.override_reason = payload.get("reason", "Manual override")
    option.overridden_by = "usr_ops1" # mock user
    await db.commit()
    return {"data": {"status": "success"}}
