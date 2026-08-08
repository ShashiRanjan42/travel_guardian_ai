from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from app.data.session import get_db
from app.data.models import Booking, Traveller
from app.api.v1.auth import get_current_user
import uuid

router = APIRouter()

@router.get("/book/destinations/search")
async def search_destinations(q: str):
    # Mock data for autocomplete
    destinations = [
        {"id": "loc_01", "name": "Manali, Himachal Pradesh", "type": "city"},
        {"id": "loc_02", "name": "Shimla, Himachal Pradesh", "type": "city"},
        {"id": "loc_03", "name": "Kasol, Himachal Pradesh", "type": "city"}
    ]
    results = [d for d in destinations if q.lower() in d["name"].lower()]
    return {"data": results}

@router.post("/book/draft")
async def create_draft(payload: dict, db = Depends(get_db), user: dict = Depends(get_current_user)):
    if user["role"] != "traveller":
        raise HTTPException(status_code=403, detail="Traveller role required")
        
    draft_id = f"draft_{uuid.uuid4().hex[:8]}"
    return {
        "data": {
            "draft_id": draft_id,
            "status": "DRAFT",
            "origin": payload.get("origin"),
            "destination": payload.get("destination"),
            "dates": payload.get("dates")
        }
    }

@router.get("/book/draft/{id}")
async def get_draft(id: str, db = Depends(get_db), user: dict = Depends(get_current_user)):
    if user["role"] != "traveller":
        raise HTTPException(status_code=403, detail="Traveller role required")
        
    return {
        "data": {
            "draft_id": id,
            "status": "DRAFT",
            "itinerary_preview": [],
            "total_estimated_inr": 15000
        }
    }

@router.post("/book/draft/{id}/confirm")
async def confirm_draft(id: str, payload: dict, db = Depends(get_db), user: dict = Depends(get_current_user)):
    if user["role"] != "traveller":
        raise HTTPException(status_code=403, detail="Traveller role required")
        
    pnr = "W" + uuid.uuid4().hex[:6].upper()
    return {
        "data": {
            "booking_id": f"bkg_{uuid.uuid4().hex[:8]}",
            "pnr": pnr,
            "status": "CONFIRMED"
        }
    }
