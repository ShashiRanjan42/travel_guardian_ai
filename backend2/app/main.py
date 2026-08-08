from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth import router as auth_router
from app.api.v1.ops import router as ops_router
from app.api.v1.traveller import router as traveller_router
from app.api.v1.demo import router as demo_router
from app.api.v1.ws import router as ws_router
from app.api.v1.booking import router as booking_router
from app.api.v1.weather import router as weather_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.agents import router as agents_router

from contextlib import asynccontextmanager
from app.services.journey_monitor import global_monitor

@asynccontextmanager
async def lifespan(app: FastAPI):
    global_monitor.start()
    yield
    global_monitor.stop()

app = FastAPI(title="Wayfare API", version="1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # for hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(ops_router, prefix="/api/v1")
app.include_router(traveller_router, prefix="/api/v1")
app.include_router(demo_router, prefix="/api/v1")
app.include_router(ws_router, prefix="/api/v1")
app.include_router(booking_router, prefix="/api/v1")
app.include_router(weather_router, prefix="/api/v1")
app.include_router(inventory_router, prefix="/api/v1")
app.include_router(agents_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "db": "ok",
        "llm_provider": "mock", # initially mock
        "weather_provider": "open-meteo (live, no API key)",
        "version": "1.0"
    }

# Ensure envelope wrapper is used across the API in subsequent phases
