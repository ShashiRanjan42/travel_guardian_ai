import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Travel Guardian AI"
    DATABASE_URL: str = "sqlite:///./travel_guardian.db"
    
    # External APIs
    OPEN_METEO_URL: str = "https://api.open-meteo.com/v1/forecast"
    NOMINATIM_URL: str = "https://nominatim.openstreetmap.org"
    OSRM_URL: str = "https://router.project-osrm.org"
    OVERPASS_URL: str = "https://overpass-api.de/api/interpreter"
    NASA_EONET_URL: str = "https://eonet.gsfc.nasa.gov/api/v3/events"
    
    class Config:
        case_sensitive = True

settings = Settings()
