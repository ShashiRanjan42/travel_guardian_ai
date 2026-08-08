import json
import asyncio
from typing import Dict, Any, Optional

class MockLLMClient:
    async def generate(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> str:
        await asyncio.sleep(0.5) # simulate latency

        # For Replanner logic (generating options)
        if "REPLANNER" in prompt:
            if "Bhuntar" in prompt or "SCN-01" in prompt:
                options = [
                    {
                        "rank": 1,
                        "label": "Via Manali",
                        "summary": "Reroute bus via Manali.",
                        "cost_delta_inr": 1200,
                        "time_delta_minutes": 180,
                        "risk_score": 0.22,
                        "confidence": 0.87,
                        "evidence": [{"source": "Vendor API", "claim": "HR bus available via Manali"}],
                        "assumptions": ["Manali route remains open"],
                        "tradeoffs": "3h later arrival",
                        "legs": [
                            {"action": "MODIFIED", "seq": 3, "mode": "BUS", "dest_name": "Manali", "cost_inr": 1650, "booking_ref": "HR-MOD"},
                            {"action": "ADDED", "seq": 3, "mode": "CAB", "origin_name": "Manali", "dest_name": "Kasol", "cost_inr": 1000, "booking_ref": ""}
                        ]
                    },
                    {
                        "rank": 2,
                        "label": "Delay 1 day",
                        "summary": "Travel one day later.",
                        "cost_delta_inr": 0,
                        "time_delta_minutes": 1440,
                        "risk_score": 0.08,
                        "confidence": 0.94,
                        "evidence": [{"source": "HP PWD", "claim": "Road clears in 24-48h"}],
                        "assumptions": ["Clearance completes on time"],
                        "tradeoffs": "Lose first day",
                        "legs": [
                            {"action": "MODIFIED", "seq": 3, "mode": "BUS", "depart_at_offset_hours": 24, "arrive_at_offset_hours": 24}
                        ]
                    },
                    {
                        "rank": 3,
                        "label": "Via Jalori",
                        "summary": "Alternative mountain pass.",
                        "cost_delta_inr": 800,
                        "time_delta_minutes": 240,
                        "risk_score": 0.65,
                        "confidence": 0.70,
                        "evidence": [{"source": "Maps", "claim": "Jalori pass route exists"}],
                        "assumptions": ["Jalori is passable for buses"],
                        "tradeoffs": "High risk due to weather",
                        "legs": [
                            {"action": "MODIFIED", "seq": 3, "mode": "BUS", "waypoints": [{"lat": 31.54, "lon": 77.36}]}
                        ]
                    }
                ]
                return json.dumps({"options": options})

        # For Compliance logic (understanding advisory impact)
        if "COMPLIANCE" in prompt:
            if "Jalori" in prompt:
                # Mocking rule C-01 rejection interpretation
                return json.dumps({"interpreted_risk": "HIGH", "rule": "C-01"})
            return json.dumps({"interpreted_risk": "LOW", "rule": None})

        return "{}"
