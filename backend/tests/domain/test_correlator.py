import pytest
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from typing import List, Optional
from app.domain.agents.correlator import Correlator

@dataclass
class MockEvent:
    affected_modes: List[str]
    start_time: datetime
    end_time: datetime
    geo_center_lat: float
    geo_center_lon: float
    radius_km: float

@dataclass
class MockLeg:
    id: str
    mode: str
    depart_at: datetime
    arrive_at: datetime
    origin_lat: float
    origin_lon: float
    dest_lat: float
    dest_lon: float
    waypoints: List[dict]
    depends_on_leg_id: Optional[str]

def test_correlator_deterministic_matching():
    correlator = Correlator()
    
    event = MockEvent(
        affected_modes=["BUS", "CAB"],
        start_time=datetime(2026, 8, 8, 10, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 8, 10, 10, 0, tzinfo=timezone.utc),
        geo_center_lat=31.88,
        geo_center_lon=77.15,
        radius_km=25.0
    )
    
    # Matching leg
    leg_match = MockLeg(
        id="leg_1",
        mode="BUS",
        depart_at=datetime(2026, 8, 8, 20, 0, tzinfo=timezone.utc),
        arrive_at=datetime(2026, 8, 9, 8, 30, tzinfo=timezone.utc),
        origin_lat=28.66, origin_lon=77.22,
        dest_lat=32.01, dest_lon=77.31,
        waypoints=[{"lat": 31.88, "lon": 77.15}],
        depends_on_leg_id=None
    )
    
    # Non-matching mode
    leg_flight = MockLeg(
        id="leg_2", mode="FLIGHT",
        depart_at=datetime(2026, 8, 8, 20, 0, tzinfo=timezone.utc), arrive_at=datetime(2026, 8, 9, 8, 30, tzinfo=timezone.utc),
        origin_lat=31.88, origin_lon=77.15, dest_lat=32.01, dest_lon=77.31,
        waypoints=[], depends_on_leg_id=None
    )
    
    # Cascade dependent leg
    leg_cascade = MockLeg(
        id="leg_3", mode="HOTEL",
        depart_at=datetime(2026, 8, 9, 12, 0, tzinfo=timezone.utc), arrive_at=datetime(2026, 8, 9, 12, 0, tzinfo=timezone.utc),
        origin_lat=32.01, origin_lon=77.31, dest_lat=32.01, dest_lon=77.31,
        waypoints=[], depends_on_leg_id="leg_1"
    )

    result = correlator.evaluate(event, [leg_match, leg_flight, leg_cascade])
    
    assert result["status"] == "success"
    assert "leg_1" in result["direct_match_ids"]
    assert "leg_2" not in result["direct_match_ids"]
    assert "leg_3" in result["cascade_match_ids"]

def test_correlator_performance_312_legs():
    correlator = Correlator()
    
    event = MockEvent(
        affected_modes=["BUS", "CAB"],
        start_time=datetime(2026, 8, 8, 10, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 8, 10, 10, 0, tzinfo=timezone.utc),
        geo_center_lat=31.88,
        geo_center_lon=77.15,
        radius_km=25.0
    )
    
    legs = []
    # 1 matching leg with 3 cascades
    legs.append(MockLeg(
        id="leg_match", mode="BUS",
        depart_at=datetime(2026, 8, 8, 20, 0, tzinfo=timezone.utc), arrive_at=datetime(2026, 8, 9, 8, 30, tzinfo=timezone.utc),
        origin_lat=28.66, origin_lon=77.22, dest_lat=32.01, dest_lon=77.31,
        waypoints=[{"lat": 31.88, "lon": 77.15}], depends_on_leg_id=None
    ))
    legs.append(MockLeg(
        id="leg_casc_1", mode="HOTEL",
        depart_at=datetime(2026, 8, 9, 12, 0, tzinfo=timezone.utc), arrive_at=datetime(2026, 8, 9, 12, 0, tzinfo=timezone.utc),
        origin_lat=0, origin_lon=0, dest_lat=0, dest_lon=0, waypoints=[], depends_on_leg_id="leg_match"
    ))
    legs.append(MockLeg(
        id="leg_casc_2", mode="ACTIVITY",
        depart_at=datetime(2026, 8, 9, 16, 0, tzinfo=timezone.utc), arrive_at=datetime(2026, 8, 9, 18, 0, tzinfo=timezone.utc),
        origin_lat=0, origin_lon=0, dest_lat=0, dest_lon=0, waypoints=[], depends_on_leg_id="leg_casc_1"
    ))
    legs.append(MockLeg(
        id="leg_casc_3", mode="ACTIVITY",
        depart_at=datetime(2026, 8, 10, 6, 0, tzinfo=timezone.utc), arrive_at=datetime(2026, 8, 10, 19, 0, tzinfo=timezone.utc),
        origin_lat=0, origin_lon=0, dest_lat=0, dest_lon=0, waypoints=[], depends_on_leg_id="leg_casc_1"
    ))

    # Add 308 non-matching noise legs
    for i in range(308):
        mode = "FLIGHT" if i % 2 == 0 else "TRAIN"
        legs.append(MockLeg(
            id=f"noise_{i}", mode=mode,
            depart_at=datetime(2026, 8, 8, 12, 0, tzinfo=timezone.utc), arrive_at=datetime(2026, 8, 8, 14, 0, tzinfo=timezone.utc),
            origin_lat=10.0, origin_lon=10.0, dest_lat=20.0, dest_lon=20.0,
            waypoints=[], depends_on_leg_id=None
        ))
        
    result = correlator.evaluate(event, legs)
    
    assert result["status"] == "success"
    assert "leg_match" in result["direct_match_ids"]
    assert "leg_casc_1" in result["cascade_match_ids"]
    assert "leg_casc_2" in result["cascade_match_ids"]
    assert "leg_casc_3" in result["cascade_match_ids"]
    
    print(f"\n312-legs performance case completed in {result['duration_ms']}ms")
    assert result["duration_ms"] < 100 # Should be extremely fast
