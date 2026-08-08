import httpx
from langchain_core.tools import tool
from typing import Optional

from app.services.transport_inventory import search_flights as db_search_flights
from app.services.transport_inventory import search_hotels as db_search_hotels
from app.services.transport_inventory import search_trains as db_search_trains

@tool
def search_flights(origin: str, destination: str) -> str:
    """
    Search for alternative flights between an origin and destination city.
    Returns a JSON string of available flights including price, carrier, and timings.
    """
    results = db_search_flights(origin, destination)
    import json
    return json.dumps(results)

@tool
def search_hotels(city: str) -> str:
    """
    Search for alternative hotels in a specific city for layovers or overnight stays.
    Returns a JSON string of available hotels including price, rating, and amenities.
    """
    results = db_search_hotels(city)
    import json
    return json.dumps(results)

@tool
def search_trains(origin: str, destination: str) -> str:
    """
    Search for alternative trains between an origin and destination city.
    Returns a JSON string of available trains including price, class, and timings.
    """
    results = db_search_trains(origin, destination)
    import json
    return json.dumps(results)

@tool
def check_weather(latitude: float, longitude: float) -> str:
    """
    Check current and forecasted weather for a specific latitude and longitude.
    Useful for determining if a disruption (e.g. thunderstorm) is ongoing at a location.
    """
    try:
        # Using synchronous httpx for tool simplicity
        response = httpx.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true",
            timeout=5.0
        )
        if response.status_code == 200:
            import json
            return json.dumps(response.json().get("current_weather", {}))
        return '{"error": "Weather data unavailable"}'
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'
