import math
import time
from typing import List, Dict, Any, Set
from dataclasses import dataclass
from datetime import datetime
from app.integrations.llm.base import LLMClient

# We will just define minimal dataclasses for testing, but in prod it uses SQLAlchemy models.
# Since the correlator is a pure function / domain logic, it's best to abstract it.

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0 # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def time_overlap(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
    return max(start1, start2) <= min(end1, end2)

class Correlator:
    def __init__(self, llm_client: LLMClient | None = None):
        self.name = "CORRELATOR"
        self.llm_client = llm_client

    async def explain(self, event, result: Dict[str, Any]) -> str:
        """Use the LLM for an auditable explanation, never for the match decision."""
        fallback = "Deterministic matching used affected mode, event time window, and geographic radius."
        if self.llm_client is None:
            return fallback
        prompt = f"""Explain this travel-disruption correlation in two concise sentences for an operations agent.
Do not claim facts not in the data and do not change the matching result.
Event: {event.headline}; affected modes: {event.affected_modes}; radius: {event.radius_km} km.
Direct matches: {len(result['direct_match_ids'])}; downstream matches: {len(result['cascade_match_ids'])}."""
        try:
            return await self.llm_client.generate(prompt)
        except RuntimeError:
            return fallback

    def evaluate(self, event, legs) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. Mode Gate
        affected_modes = set(event.affected_modes)
        
        direct_matches = []
        for leg in legs:
            if leg.mode not in affected_modes:
                continue
            
            # 2. Time Gate
            if not time_overlap(leg.depart_at, leg.arrive_at, event.start_time, event.end_time):
                continue
                
            # 3. Geo Gate
            # check origin, dest, and waypoints
            points_to_check = [(leg.origin_lat, leg.origin_lon), (leg.dest_lat, leg.dest_lon)]
            if leg.waypoints:
                for wp in leg.waypoints:
                    points_to_check.append((wp['lat'], wp['lon']))
                    
            matched_geo = False
            for lat, lon in points_to_check:
                dist = haversine(lat, lon, event.geo_center_lat, event.geo_center_lon)
                if dist <= event.radius_km:
                    matched_geo = True
                    break
                    
            if matched_geo:
                direct_matches.append(leg)

        # 4. Cascade Resolver
        # build dependency graph
        dependent_legs = {leg.id: [] for leg in legs}
        for leg in legs:
            if leg.depends_on_leg_id:
                dependent_legs[leg.depends_on_leg_id].append(leg.id)
                
        def get_all_downstream(leg_id: str, visited: Set[str]) -> Set[str]:
            for down_id in dependent_legs.get(leg_id, []):
                if down_id not in visited:
                    visited.add(down_id)
                    get_all_downstream(down_id, visited)
            return visited

        cascade_match_ids = set()
        for leg in direct_matches:
            downstream = get_all_downstream(leg.id, set())
            cascade_match_ids.update(downstream)

        # Remove direct matches from cascade matches just in case
        direct_ids = {leg.id for leg in direct_matches}
        cascade_match_ids = cascade_match_ids - direct_ids

        duration_ms = int((time.time() - start_time) * 1000)
        
        return {
            "agent": self.name,
            "status": "success" if (direct_matches or cascade_match_ids) else "skipped",
            "direct_match_ids": list(direct_ids),
            "cascade_match_ids": list(cascade_match_ids),
            "duration_ms": duration_ms
        }
