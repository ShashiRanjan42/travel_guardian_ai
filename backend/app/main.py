import asyncio
import json
import logging
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, SessionLocal
from app.models.models import User, Customer, Itinerary, ItineraryLeg, Incident, RecoveryPlan, AgentLog
from app.routers import itineraries, incidents, agents, simulate, analytics, auth, inventory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

def seed_database():
    """Seed DB with brand new 15 Indian Customer itineraries & Auth Users"""
    db = SessionLocal()
    try:
        if db.query(Customer).count() >= 10:
            return

        logger.info("Seeding BRAND NEW Indian Customer Dummy Data...")

        # 1. Ops Team Lead User
        u_ops = User(
            id="usr-ops-1",
            name="Priya Nair (Ops Lead)",
            email="ops@guardian.ai",
            password="admin",
            role="OPS",
            tier="Executive Ops Lead"
        )
        db.add(u_ops)

        # Brand New Indian Dummy Customers List
        new_indian_customers_data = [
            {"id": "cust-1", "name": "Aarav Singhania", "email": "aarav.singhania@reliance.com", "tier": "VIP", "city": "Mumbai", "route": "Mumbai - Delhi - Srinagar", "risk": 95, "level": "CRITICAL"},
            {"id": "cust-2", "name": "Diya Sharma", "email": "diya.sharma@tata.com", "tier": "VIP", "city": "Bengaluru", "route": "Bengaluru - Hyderabad - Goa", "risk": 85, "level": "HIGH"},
            {"id": "cust-3", "name": "Kabir Mehta", "email": "kabir.mehta@infosys.com", "tier": "Platinum", "city": "Delhi", "route": "Delhi - Jaipur - Udaipur", "risk": 60, "level": "ELEVATED"},
            {"id": "cust-4", "name": "Rhea Banerjee", "email": "rhea.banerjee@tcs.com", "tier": "VIP", "city": "Kolkata", "route": "Kolkata - Bhubaneswar - Chennai", "risk": 20, "level": "LOW"},
            {"id": "cust-5", "name": "Ishan Verma", "email": "ishan.verma@zomato.in", "tier": "Gold", "city": "Chandigarh", "route": "Chandigarh - Delhi - Pune", "risk": 15, "level": "LOW"},
            {"id": "cust-6", "name": "Tara Deshmukh", "email": "tara.d@serum.org", "tier": "VIP", "city": "Pune", "route": "Pune - Mumbai - Ahmedabad", "risk": 15, "level": "LOW"},
            {"id": "cust-7", "name": "Devansh Joshi", "email": "devansh.j@adani.com", "tier": "Platinum", "city": "Ahmedabad", "route": "Ahmedabad - Rajkot - Mumbai", "risk": 10, "level": "LOW"},
            {"id": "cust-8", "name": "Anvi Kulkarni", "email": "anvi.k@eicher.in", "tier": "Gold", "city": "Indore", "route": "Indore - Bhopal - Delhi", "risk": 10, "level": "LOW"},
            {"id": "cust-9", "name": "Vihaan Reddy", "email": "vihaan.r@drreddy.com", "tier": "Standard", "city": "Hyderabad", "route": "Hyderabad - Vijayawada - Visakhapatnam", "risk": 10, "level": "LOW"},
            {"id": "cust-10", "name": "Sanvi Pillai", "email": "sanvi.p@wipro.com", "tier": "VIP", "city": "Kochi", "route": "Kochi - Trivandrum - Chennai", "risk": 10, "level": "LOW"},
            {"id": "cust-11", "name": "Yashwardhan Chawla", "email": "yash.chawla@hero.in", "tier": "Platinum", "city": "Lucknow", "route": "Lucknow - Varanasi - Delhi", "risk": 10, "level": "LOW"},
            {"id": "cust-12", "name": "Nisha Swaminathan", "email": "nisha.s@titan.in", "tier": "Standard", "city": "Coimbatore", "route": "Coimbatore - Bengaluru - Mysuru", "risk": 10, "level": "LOW"},
            {"id": "cust-13", "name": "Rohan Sengupta", "email": "rohan.s@oilindia.in", "tier": "Gold", "city": "Guwahati", "route": "Guwahati - Shillong - Kolkata", "risk": 10, "level": "LOW"},
            {"id": "cust-14", "name": "Avani Mittal", "email": "avani.m@dabur.com", "tier": "VIP", "city": "Dehradun", "route": "Dehradun - Delhi - Mumbai", "risk": 10, "level": "LOW"},
            {"id": "cust-15", "name": "Manish Agrawal", "email": "manish.a@suratgems.in", "tier": "Platinum", "city": "Surat", "route": "Surat - Mumbai - Bengaluru", "risk": 10, "level": "LOW"}
        ]

        for idx, item in enumerate(new_indian_customers_data):
            # User Auth Entity
            u = User(
                id=f"usr-{item['id']}",
                name=item["name"],
                email=item["email"],
                password="pass",
                role="CUSTOMER",
                tier=item["tier"]
            )
            db.add(u)

            # Customer Entity
            c = Customer(
                id=item["id"],
                name=item["name"],
                email=item["email"],
                phone=f"+91 98765 {20000 + idx}",
                tier=item["tier"],
                home_city=item["city"],
                preferences=json.dumps({"seat": "Window", "hotel": "5-Star Executive Suite", "meal": "Jain Meal"})
            )
            db.add(c)
            db.commit()

            # Itinerary Entity
            it = Itinerary(
                id=f"itinerary-{idx+1}",
                customer_id=item["id"],
                title=f"{item['name']} — {item['route']}",
                status="DISRUPTED" if item["risk"] >= 80 else ("WARNING" if item["risk"] >= 50 else "OK"),
                risk_score=item["risk"],
                risk_level=item["level"],
                start_date=datetime.utcnow() + timedelta(days=idx),
                end_date=datetime.utcnow() + timedelta(days=idx+4)
            )
            db.add(it)
            db.commit()

            # Travel Legs
            leg1 = ItineraryLeg(
                id=f"leg-{idx+1}01",
                itinerary_id=it.id,
                sequence_order=1,
                leg_type="FLIGHT",
                title=f"Air India AI-{800+idx} • {item['city']} to Delhi (DEL)",
                operator="Air India",
                code=f"AI-{800+idx}",
                origin=f"{item['city']} Airport",
                destination="Delhi (DEL)",
                origin_lat=19.0896 if item['city']=="Mumbai" else (13.1986 if item['city']=="Bengaluru" else 28.5562),
                origin_lon=72.8656 if item['city']=="Mumbai" else (77.7066 if item['city']=="Bengaluru" else 77.1000),
                dest_lat=28.5562,
                dest_lon=77.1000,
                departure_time=datetime.utcnow() + timedelta(hours=2+idx),
                arrival_time=datetime.utcnow() + timedelta(hours=4.5+idx),
                status="DELAYED" if item["risk"] >= 80 else "SCHEDULED",
                details_json=json.dumps({"seat": "2A Business Class", "aircraft": "Boeing 787 Dreamliner", "terminal": "T3"})
            )

            leg2 = ItineraryLeg(
                id=f"leg-{idx+1}02",
                itinerary_id=it.id,
                sequence_order=2,
                leg_type="TRAIN",
                title=f"Vande Bharat Express • Delhi to Srinagar / Goa Line",
                operator="Indian Railways",
                code=f"VB-224{idx%9}",
                origin="Delhi Junction",
                destination="Srinagar / Regional Station",
                origin_lat=28.5562,
                origin_lon=77.1000,
                dest_lat=34.0837,
                dest_lon=74.7973,
                departure_time=datetime.utcnow() + timedelta(hours=6+idx),
                arrival_time=datetime.utcnow() + timedelta(hours=14+idx),
                status="SCHEDULED",
                details_json=json.dumps({"coach": "Executive EC", "seat": "E2-14", "class": "Executive Chair Car"})
            )

            leg3 = ItineraryLeg(
                id=f"leg-{idx+1}03",
                itinerary_id=it.id,
                sequence_order=3,
                leg_type="HOTEL",
                title=f"Taj Palace Delhi & The Oberoi Grand",
                operator="Taj Hotels / Oberoi Group",
                code=f"TAJ-VALLEY-{900+idx}",
                origin="Srinagar Station",
                destination="Taj Palace Hotel Suite",
                origin_lat=34.0837,
                origin_lon=74.7973,
                dest_lat=34.0900,
                dest_lon=74.8000,
                departure_time=datetime.utcnow() + timedelta(hours=15+idx),
                arrival_time=datetime.utcnow() + timedelta(days=3+idx),
                status="SCHEDULED",
                details_json=json.dumps({"room": "Heritage Presidential Suite", "late_checkout": True})
            )
            db.add_all([leg1, leg2, leg3])
            db.commit()

        # Seed initial High Risk Incidents for Aarav Singhania & Diya Sharma
        inc1 = Incident(
            id="INC-IND-201",
            itinerary_id="itinerary-1",
            leg_id="leg-101",
            title="Alpine Blizzard & Highway Landslide Block — Srinagar Sector",
            type="WEATHER",
            severity="CRITICAL",
            status="RECOVERY_PROPOSED",
            description="Heavy snowfall and 100 km/h blizzard gusts close Srinagar runway and highway pass. Air India flight delayed 4 hours.",
            impact_summary="Primary flight leg delayed by 4h. Mountain rail connection window compromised.",
            lat=34.0837,
            lon=74.7973,
            detected_at=datetime.utcnow()
        )
        db.add(inc1)

        plan1_a = RecoveryPlan(
            id="PLAN-INC-IND-201-1",
            incident_id="INC-IND-201",
            option_code="OPTION_A",
            title="Express Helicopter Transfer to Taj Suite + Vande Bharat Priority Seat",
            summary="Pivot to Himalayan Heli Chauffeur transfer directly to Taj Palace Srinagar with zero highway delay.",
            cost_delta=0.0,
            eta_delta_minutes=25,
            confidence_score=0.98,
            reasoning="98% AI confidence. Bypasses mountain highway closures. Covered under VIP Tier protection.",
            tradeoffs="15-minute helipad transfer at Delhi hub.",
            actions_json=json.dumps([{"step": 1, "desc": "Reserve Himalayan Air VIP Heli-Chauffeur"}, {"step": 2, "desc": "Confirm Taj Suite Check-in Guarantee"}]),
            status="PROPOSED"
        )
        plan1_b = RecoveryPlan(
            id="PLAN-INC-IND-201-2",
            incident_id="INC-IND-201",
            option_code="OPTION_B",
            title="Air India Next Morning Priority Rebook AI-810",
            summary="Overnight stay at Taj Palace Delhi, followed by 07:00 AM priority flight to Srinagar.",
            cost_delta=320.0,
            eta_delta_minutes=240,
            confidence_score=0.90,
            reasoning="High safety reliability once mountain blizzard cell passes.",
            tradeoffs="Adds overnight hotel stay in Delhi.",
            actions_json=json.dumps([{"step": 1, "desc": "Book Taj Palace Delhi Executive Suite"}]),
            status="PROPOSED"
        )
        db.add_all([plan1_a, plan1_b])

        inc2 = Incident(
            id="INC-IND-202",
            itinerary_id="itinerary-2",
            leg_id="leg-201",
            title="Coastal Cyclone Alert & Heavy Gale Winds — Goa / Coastal Corridor",
            type="DISASTER",
            severity="HIGH",
            status="RECOVERY_PROPOSED",
            description="Coastal cyclone alert reduces airport runway capacity at Dabolim Goa. Flights holding in air pattern.",
            impact_summary="Bengaluru-Goa flight delayed by 2.5 hours.",
            lat=15.3808,
            lon=73.8314,
            detected_at=datetime.utcnow()
        )
        db.add(inc2)

        logger.info("Seeding NEW Indian Customer Dummy Data completed successfully.")

    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_database()
    logger.info("Travel Guardian AI Backend (New Data Edition) initialized.")
    yield

app = FastAPI(
    title="Travel Guardian AI Backend — New Data Edition",
    description="Multi-Agent Protective Travel System powered by LangGraph & FastAPI",
    version="3.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(itineraries.router)
app.include_router(incidents.router)
app.include_router(agents.router)
app.include_router(simulate.router)
app.include_router(analytics.router)
app.include_router(inventory.router)

@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "Travel Guardian AI Backend (New Dummy Data)",
        "customers_seeded": 15,
        "agents_online": 7,
        "timestamp": datetime.utcnow().isoformat()
    }
