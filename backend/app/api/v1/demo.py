import asyncio
import json
import os
from dateutil.parser import isoparse
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.data.session import get_db, AsyncSessionLocal
from app.data.models import DisruptionEvent
from app.domain.agents.orchestrator import Orchestrator
from app.security.injection_guard import guard
from sqlalchemy import select

router = APIRouter()
orchestrator = Orchestrator()

@router.post("/demo/inject-disruption")
async def inject_scenario(payload: dict, background_tasks: BackgroundTasks, db = Depends(get_db)):
    scenario_id = payload.get("scenario_id")
    
    # Load scenarios
    scenarios_path = os.path.join(os.path.dirname(__file__), '../../../app/data/seed/scenarios.json')
    with open(scenarios_path, 'r') as f:
        scenarios = json.load(f)
        
    scenario = next((s for s in scenarios if s["id"] == scenario_id), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
        
    sp = scenario["payload"]
    
    # Guardrail G-1: Injection Guard
    guard_result = guard(sp["description"], sp["source_name"])
    
    event = DisruptionEvent(
        type=sp["type"],
        source_name=sp["source_name"],
        source_reliability=0.9, # mock
        raw_payload=sp,
        headline=sp["headline"],
        description=guard_result.cleaned_text,
        geo_center_lat=sp["geo_center_lat"],
        geo_center_lon=sp["geo_center_lon"],
        radius_km=sp["radius_km"],
        affected_modes=sp["affected_modes"],
        start_time=isoparse(sp["start_time"]),
        end_time=isoparse(sp["end_time"]),
        severity_hint="HIGH",
        freshness="LIVE",
        injection_flagged=guard_result.flagged
    )
    db.add(event)
    await db.commit()
    
    # Kick off orchestrator in background so API returns immediately (simulating real webhook reception)
    background_tasks.add_task(orchestrator.process_event, str(event.id))
    
    return {"data": {"status": "accepted", "event_id": str(event.id), "injection_flagged": guard_result.flagged}}

@router.post("/demo/reset")
async def reset_demo():
    # In a real setup, we'd truncate tables and re-run loader.
    # We can invoke the seed function.
    from app.data.seed.loader import run as seed_run
    await seed_run()
    return {"data": {"status": "reset_successful"}}
