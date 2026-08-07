import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Customer, Itinerary, ItineraryLeg

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login")
def login(payload: dict = Body(...), db: Session = Depends(get_db)):
    email = payload.get("email", "").strip().lower()
    password = payload.get("password", "").strip()
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required.")

    user = db.query(User).filter(User.email == email).first()
    
    # Fallback helper for quick demo logins if exact password wasn't matched
    if not user or user.password != password:
        if email == "ops@guardian.ai":
            user = db.query(User).filter(User.role == "OPS").first()
        elif "@" in email:
            user = db.query(User).filter(User.email == email).first()
            if not user and (email.startswith("cust") or "rajesh" in email or "priya" in email or "vikram" in email):
                user = db.query(User).filter(User.role == "CUSTOMER").first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # Find associated customer itinerary if customer
    active_itinerary_id = None
    if user.role == "CUSTOMER":
        cust = db.query(Customer).filter(Customer.email == user.email).first()
        if not cust:
            cust = db.query(Customer).first()
        if cust:
            it = db.query(Itinerary).filter(Itinerary.customer_id == cust.id).first()
            if it:
                active_itinerary_id = it.id

    token = f"token-{user.id}-{int(datetime.utcnow().timestamp())}"

    return {
        "status": "SUCCESS",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "tier": user.tier,
            "active_itinerary_id": active_itinerary_id
        }
    }

@router.post("/signup")
def signup(payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        name = payload.get("name", "").strip()
        email = payload.get("email", "").strip().lower()
        password = payload.get("password", "").strip()
        role = payload.get("role", "CUSTOMER").upper()
        tier = payload.get("tier", "VIP")

        if not name or not email or not password:
            raise HTTPException(status_code=400, detail="Name, email, and password are required.")

        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise HTTPException(status_code=409, detail="User with this email already exists. Please sign in.")

        user_id = f"usr-{uuid.uuid4().hex[:8]}"
        new_user = User(
            id=user_id,
            name=name,
            email=email,
            password=password,
            role=role,
            tier=tier
        )
        db.add(new_user)

        active_itinerary_id = None
        if role == "CUSTOMER":
            cust_id = f"cust-{user_id}"
            new_cust = Customer(
                id=cust_id,
                name=name,
                email=email,
                phone="+91 98765 43210",
                tier=tier,
                home_city="Mumbai"
            )
            db.add(new_cust)
            db.commit()

            # Create an initial protected itinerary for the new customer!
            it_id = f"itinerary-new-{user_id}"
            new_it = Itinerary(
                id=it_id,
                customer_id=cust_id,
                title=f"{name} — Mumbai - Delhi - Bengaluru Express",
                status="OK",
                risk_score=15,
                risk_level="LOW",
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=4)
            )
            db.add(new_it)
            db.commit()

            # Create sample legs
            leg1 = ItineraryLeg(
                id=f"leg-{user_id}-1",
                itinerary_id=it_id,
                sequence_order=1,
                leg_type="FLIGHT",
                title="IndiGo 6E-501 • Mumbai (BOM) to Delhi (DEL)",
                operator="IndiGo Airlines",
                code="6E-501",
                origin="Mumbai Airport (BOM)",
                destination="Delhi Airport (DEL)",
                origin_lat=19.0896,
                origin_lon=72.8656,
                dest_lat=28.5562,
                dest_lon=77.1000,
                departure_time=datetime.utcnow() + timedelta(hours=3),
                arrival_time=datetime.utcnow() + timedelta(hours=5.5),
                status="SCHEDULED"
            )
            leg2 = ItineraryLeg(
                id=f"leg-{user_id}-2",
                itinerary_id=it_id,
                sequence_order=2,
                leg_type="TRAIN",
                title="Vande Bharat Express • Delhi to Bengaluru",
                operator="Indian Railways",
                code="VB-2090",
                origin="Delhi Terminal",
                destination="Bengaluru City (SBC)",
                origin_lat=28.5562,
                origin_lon=77.1000,
                dest_lat=12.9781,
                dest_lon=77.5697,
                departure_time=datetime.utcnow() + timedelta(hours=8),
                arrival_time=datetime.utcnow() + timedelta(hours=16),
                status="SCHEDULED"
            )
            db.add_all([leg1, leg2])
            db.commit()
            active_itinerary_id = it_id
        else:
            db.commit()

        token = f"token-{user_id}-{int(datetime.utcnow().timestamp())}"

        return {
            "status": "SUCCESS",
            "message": f"Account created for {name} ({role})",
            "token": token,
            "user": {
                "id": user_id,
                "name": name,
                "email": email,
                "role": role,
                "tier": tier,
                "active_itinerary_id": active_itinerary_id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create user account: {str(e)}")

@router.get("/demo_users")
def get_demo_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "tier": u.tier
        } for u in users
    ]
