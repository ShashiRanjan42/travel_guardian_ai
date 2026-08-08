import json
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.data.models import Base, User, Traveller, Booking, Itinerary, ItineraryVersion, Leg, Vendor
from app.domain.enums import UserRole, LegMode, LegStatus

engine = create_async_engine('sqlite+aiosqlite:///./wayfare.db', echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def seed_data():
    async with AsyncSessionLocal() as session:
        # Users
        ops_user = User(email="meera@wayfare.in", password_hash="hash_demo1234", role=UserRole.OPS_AGENT, full_name="Meera Iyer")
        trv_user1 = User(email="rohan@example.com", password_hash="hash_demo1234", role=UserRole.TRAVELLER, full_name="Rohan Desai")
        trv_user2 = User(email="noise@example.com", password_hash="hash", role=UserRole.TRAVELLER, full_name="Noise User")
        session.add_all([ops_user, trv_user1, trv_user2])
        await session.commit()

        # Travellers
        rohan = Traveller(user_id=trv_user1.id, full_name="Rohan Desai", phone="+91-98XXXXXX21", email="rohan@example.com", is_solo=True, vulnerability_flag="none", preferences={"cost_sensitivity": "high", "avoid_red_eye": True, "max_cost_delta_inr": 3000})
        session.add(rohan)
        await session.commit()

        # Vendors
        indigo = Vendor(name="IndiGo", type=LegMode.FLIGHT, reliability_score=0.9, supports_modes=[LegMode.FLIGHT], status="operational")
        hr = Vendor(name="Himachal Roadways", type=LegMode.BUS, reliability_score=0.82, supports_modes=[LegMode.BUS], status="operational")
        riverside = Vendor(name="Riverside Homestay", type=LegMode.HOTEL, reliability_score=0.95, supports_modes=[LegMode.HOTEL], status="operational")
        session.add_all([indigo, hr, riverside])
        await session.commit()

        # Generate 46 noise bookings
        for i in range(46):
            b = Booking(
                pnr=f"NOISE{i:03d}",
                traveller_id=rohan.id,
                ops_agent_id=ops_user.id,
                destination=f"Dest {i}",
                origin=f"Origin {i}",
                start_date=datetime(2026, 8, 8, tzinfo=timezone.utc),
                end_date=datetime(2026, 8, 12, tzinfo=timezone.utc),
                total_value_inr=10000,
                non_refundable_value_inr=5000,
                status="active",
                source="SEEDED"
            )
            session.add(b)
            await session.commit()
            it = Itinerary(booking_id=b.id, current_version=1)
            session.add(it)
            await session.commit()
            itv = ItineraryVersion(itinerary_id=it.id, version=1, created_by="SYSTEM", reason="Initial", snapshot={})
            session.add(itv)
            await session.commit()
            leg = Leg(
                itinerary_version_id=itv.id, seq=1, day_index=1, mode=LegMode.FLIGHT, status=LegStatus.CONFIRMED,
                title="Noise Leg", vendor_id=indigo.id, origin_name="A", origin_lat=0, origin_lon=0, dest_name="B", dest_lat=0, dest_lon=0,
                waypoints=[], depart_at=datetime(2026, 8, 8, 10, tzinfo=timezone.utc), arrive_at=datetime(2026, 8, 8, 12, tzinfo=timezone.utc),
                cost_inr=5000, is_refundable=False, booking_ref="REF"
            )
            session.add(leg)
            await session.commit()

        # Rohan's Booking (Demo Spine)
        rohan_booking = Booking(
            pnr="WF7K2M9Q", traveller_id=rohan.id, ops_agent_id=ops_user.id, destination="Kasol", origin="Mumbai",
            start_date=datetime(2026, 8, 8, tzinfo=timezone.utc), end_date=datetime(2026, 8, 12, tzinfo=timezone.utc),
            total_value_inr=22000, non_refundable_value_inr=16400, status="active", source="SEEDED"
        )
        session.add(rohan_booking)
        await session.commit()

        rohan_it = Itinerary(booking_id=rohan_booking.id, current_version=1)
        session.add(rohan_it)
        await session.commit()

        rohan_itv = ItineraryVersion(itinerary_id=rohan_it.id, version=1, created_by="SYSTEM", reason="Initial booking", snapshot={})
        session.add(rohan_itv)
        await session.commit()

        d1 = datetime(2026, 8, 8, tzinfo=timezone.utc)
        legs = [
            Leg(itinerary_version_id=rohan_itv.id, seq=1, day_index=1, mode=LegMode.FLIGHT, status=LegStatus.CONFIRMED, title="6E-2134 BOM→DEL",
                vendor_id=indigo.id, origin_name="BOM", origin_lat=19.08, origin_lon=72.86, dest_name="DEL", dest_lat=28.55, dest_lon=77.10, waypoints=[],
                depart_at=d1.replace(hour=14, minute=20), arrive_at=d1.replace(hour=16, minute=35), cost_inr=4800, is_refundable=False, booking_ref="6E-PNRXYZ"),
            Leg(itinerary_version_id=rohan_itv.id, seq=2, day_index=1, mode=LegMode.CAB, status=LegStatus.CONFIRMED, title="IGI T1 → Kashmiri Gate ISBT",
                vendor_id=None, origin_name="IGI T1", origin_lat=28.55, origin_lon=77.10, dest_name="ISBT", dest_lat=28.66, dest_lon=77.22, waypoints=[],
                depart_at=d1.replace(hour=17, minute=30), arrive_at=d1.replace(hour=18, minute=40), cost_inr=650, is_refundable=True, booking_ref=""),
            Leg(itinerary_version_id=rohan_itv.id, seq=3, day_index=1, mode=LegMode.BUS, status=LegStatus.CONFIRMED, title="Himachal Roadways Volvo DEL→Kasol",
                vendor_id=hr.id, origin_name="DEL", origin_lat=28.66, origin_lon=77.22, dest_name="Kasol", dest_lat=32.01, dest_lon=77.31,
                waypoints=[{"name":"Bhuntar", "lat": 31.88, "lon": 77.15}], depart_at=d1.replace(hour=20, minute=0), arrive_at=(d1 + timedelta(days=1)).replace(hour=8, minute=30),
                cost_inr=1450, is_refundable=False, booking_ref="HR-88213"),
            Leg(itinerary_version_id=rohan_itv.id, seq=4, day_index=2, mode=LegMode.HOTEL, status=LegStatus.CONFIRMED, title="Riverside Homestay, Kasol (check-in)",
                vendor_id=riverside.id, origin_name="Kasol", origin_lat=32.01, origin_lon=77.31, dest_name="Kasol", dest_lat=32.01, dest_lon=77.31, waypoints=[],
                depart_at=(d1 + timedelta(days=1)).replace(hour=12, minute=0), arrive_at=(d1 + timedelta(days=1)).replace(hour=12, minute=0), cost_inr=1800, is_refundable=False, booking_ref=""),
            Leg(itinerary_version_id=rohan_itv.id, seq=5, day_index=2, mode=LegMode.ACTIVITY, status=LegStatus.CONFIRMED, title="Chalal village walk",
                vendor_id=None, origin_name="Kasol", origin_lat=32.01, origin_lon=77.31, dest_name="Chalal", dest_lat=32.02, dest_lon=77.31, waypoints=[],
                depart_at=(d1 + timedelta(days=1)).replace(hour=16, minute=0), arrive_at=(d1 + timedelta(days=1)).replace(hour=18, minute=0), cost_inr=0, is_refundable=False, booking_ref=""),
            Leg(itinerary_version_id=rohan_itv.id, seq=6, day_index=3, mode=LegMode.ACTIVITY, status=LegStatus.CONFIRMED, title="Kheerganga trek (guided)",
                vendor_id=None, origin_name="Kasol", origin_lat=32.01, origin_lon=77.31, dest_name="Kheerganga", dest_lat=31.99, dest_lon=77.45, waypoints=[],
                depart_at=(d1 + timedelta(days=2)).replace(hour=6, minute=0), arrive_at=(d1 + timedelta(days=2)).replace(hour=19, minute=0), cost_inr=2200, is_refundable=True, booking_ref="")
        ]
        session.add_all(legs)
        await session.commit()

        # Update dependencies
        legs[3].depends_on_leg_id = legs[2].id # Hotel checkin depends on bus
        legs[4].depends_on_leg_id = legs[3].id # Walk depends on checkin
        legs[5].depends_on_leg_id = legs[3].id # Trek depends on checkin (indirectly bus)
        await session.commit()
        
async def load_scenarios():
    scenarios_path = os.path.join(os.path.dirname(__file__), 'scenarios.json')
    if os.path.exists(scenarios_path):
        with open(scenarios_path, 'r') as f:
            scenarios = json.load(f)
            # just verifying it parses successfully. We can insert into DB if required.
            return scenarios

async def run():
    await init_db()
    await seed_data()
    await load_scenarios()
    print("Database seeded successfully with 47 bookings (source='SEEDED').")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
