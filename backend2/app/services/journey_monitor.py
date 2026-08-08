import asyncio
import uuid
import httpx
from datetime import datetime, timezone
from app.data.session import AsyncSessionLocal
from app.data.models import Booking, Itinerary, ItineraryVersion, Leg, DisruptionEvent
from sqlalchemy import select
from app.domain.agents.orchestrator import Orchestrator

class GlobalJourneyMonitor:
    def __init__(self):
        self.orchestrator = Orchestrator()
        self._running = False
        self._task = None

    async def _poll_active_trips(self):
        while self._running:
            try:
                async with AsyncSessionLocal() as session:
                    # Fetch all active legs for all bookings globally
                    stmt = select(Leg, Booking).join(ItineraryVersion, Leg.version_id == ItineraryVersion.id).join(Itinerary, ItineraryVersion.itinerary_id == Itinerary.id).join(Booking, Itinerary.booking_id == Booking.id).where(Booking.status == 'active')
                    
                    result = await session.execute(stmt)
                    active_trips = result.all()
                    
                    for leg, booking in active_trips:
                        if not leg.destination:
                            continue
                            
                        # Mock weather polling for this leg's destination
                        # We use a hardcoded coordinate set for simplicity, or dummy logic
                        # In production, we'd geocode `leg.destination`
                        # Here, we'll simulate a 5% chance of a severe weather anomaly being detected for active flights
                        if leg.leg_type == "FLIGHT":
                            # Simulate calling Open-Meteo or Aviation API
                            import random
                            if random.random() < 0.05:
                                # Anomaly detected! Generate a disruption event globally for this user
                                event = DisruptionEvent(
                                    id=uuid.uuid4(),
                                    type="WEATHER",
                                    headline=f"Severe Thunderstorms at {leg.destination}",
                                    description=f"Automated monitor detected severe weather anomaly affecting {leg.destination} airport. Significant delays expected.",
                                    source="GlobalJourneyMonitor (Open-Meteo Integration)",
                                    affected_modes=["FLIGHT"],
                                    detected_at=datetime.now(timezone.utc)
                                )
                                session.add(event)
                                await session.commit()
                                
                                # Trigger orchestrator
                                await self.orchestrator.process_event(str(event.id))
                                
            except Exception as e:
                print(f"GlobalJourneyMonitor Error: {e}")
                
            # Poll every 60 seconds
            await asyncio.sleep(60)

    def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._poll_active_trips())
            print("Global Journey Monitor started... monitoring all user itineraries.")

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            
global_monitor = GlobalJourneyMonitor()
