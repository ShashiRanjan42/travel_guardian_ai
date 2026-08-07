from fastapi import APIRouter, Query
from typing import Optional
from app.services.transport_inventory import search_flights, search_hotels, search_trains, search_buses

router = APIRouter(prefix="/api/inventory", tags=["inventory"])

@router.get("/flights")
def get_flights(origin: Optional[str] = None, destination: Optional[str] = None):
    return search_flights(origin, destination)

@router.get("/hotels")
def get_hotels(city: Optional[str] = None):
    return search_hotels(city)

@router.get("/trains")
def get_trains(origin: Optional[str] = None, destination: Optional[str] = None):
    return search_trains(origin, destination)

@router.get("/buses")
def get_buses(origin: Optional[str] = None, destination: Optional[str] = None):
    return search_buses(origin, destination)
