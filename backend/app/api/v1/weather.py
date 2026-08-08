"""Endpoints backed by live Open-Meteo weather observations."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import select

from app.data.models import DisruptionEvent, Leg
from app.data.session import get_db
from app.domain.agents.orchestrator import Orchestrator
from app.integrations.weather.open_meteo import (
    WeatherProviderError,
    get_current_conditions,
    safety_risk,
    weather_code_label,
)


router = APIRouter(tags=["weather"])
orchestrator = Orchestrator()


@router.get("/weather/current")
async def current_weather(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
):
    """Return real current conditions from Open-Meteo; no database write occurs."""
    try:
        observation = await get_current_conditions(latitude, longitude)
    except (ValueError, WeatherProviderError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    is_risky, severity, reason = safety_risk(observation)
    return {"data": {**observation.as_dict(), "condition": weather_code_label(observation.weather_code), "is_travel_risk": is_risky, "severity": severity, "assessment_reason": reason}}


@router.post("/weather/check-leg/{leg_id}")
async def check_leg_weather(leg_id: str, background_tasks: BackgroundTasks, db=Depends(get_db)):
    """Check a real leg's origin weather and alert the agent pipeline only if hazardous."""
    try:
        leg_uuid = UUID(leg_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="leg_id must be a UUID") from exc

    result = await db.execute(select(Leg).where(Leg.id == leg_uuid))
    leg = result.scalar_one_or_none()
    if not leg:
        raise HTTPException(status_code=404, detail="Itinerary leg not found")

    try:
        observation = await get_current_conditions(leg.origin_lat, leg.origin_lon)
    except (ValueError, WeatherProviderError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    is_risky, severity, reason = safety_risk(observation)
    response = {"data": {"leg_id": str(leg.id), "origin": leg.origin_name, "weather": observation.as_dict(), "condition": weather_code_label(observation.weather_code), "is_travel_risk": is_risky, "severity": severity, "assessment_reason": reason, "alert_created": False}}
    if not is_risky:
        return response

    now = datetime.now(timezone.utc)
    event = DisruptionEvent(
        type="WEATHER", source_name="Open-Meteo", source_url=observation.source_url,
        source_reliability=0.85, raw_payload=observation.as_dict(),
        headline=f"{weather_code_label(observation.weather_code)} near {leg.origin_name}",
        description=f"Live Open-Meteo observation indicates {reason} at {leg.origin_name}.",
        geo_center_lat=leg.origin_lat, geo_center_lon=leg.origin_lon, radius_km=25,
        affected_modes=[leg.mode], start_time=now, end_time=now + timedelta(hours=2),
        severity_hint=severity, freshness="LIVE", injection_flagged=False, detected_at=now,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    background_tasks.add_task(orchestrator.process_event, str(event.id))
    response["data"].update({"alert_created": True, "event_id": str(event.id)})
    return response
