"""No-key client for Open-Meteo's live current-conditions endpoint."""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, dataclass
from urllib.parse import urlencode
from urllib.request import urlopen


BASE_URL = "https://api.open-meteo.com/v1/forecast"
CURRENT_FIELDS = (
    "temperature_2m,apparent_temperature,precipitation,rain,showers,"
    "snowfall,weather_code,wind_speed_10m,wind_gusts_10m,visibility"
)


class WeatherProviderError(RuntimeError):
    """Raised when the weather provider cannot return a usable observation."""


@dataclass(frozen=True)
class WeatherObservation:
    latitude: float
    longitude: float
    observed_at: str
    temperature_c: float | None
    apparent_temperature_c: float | None
    precipitation_mm: float | None
    weather_code: int | None
    wind_speed_kmh: float | None
    wind_gusts_kmh: float | None
    visibility_m: float | None
    source_url: str

    def as_dict(self) -> dict:
        return asdict(self)


def weather_code_label(code: int | None) -> str:
    """Return a concise WMO weather-code description for the API response."""
    labels = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Rime fog", 51: "Light drizzle", 53: "Drizzle",
        55: "Heavy drizzle", 56: "Freezing drizzle", 57: "Heavy freezing drizzle",
        61: "Slight rain", 63: "Rain", 65: "Heavy rain", 66: "Freezing rain",
        67: "Heavy freezing rain", 71: "Slight snow", 73: "Snow", 75: "Heavy snow",
        77: "Snow grains", 80: "Rain showers", 81: "Heavy rain showers",
        82: "Violent rain showers", 85: "Snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm with hail",
    }
    return labels.get(code, "Unknown weather condition")


async def get_current_conditions(latitude: float, longitude: float) -> WeatherObservation:
    """Fetch current model-derived conditions from Open-Meteo without an API key."""
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError("latitude must be between -90 and 90; longitude between -180 and 180")

    query = urlencode({"latitude": latitude, "longitude": longitude, "current": CURRENT_FIELDS, "timezone": "UTC"})
    url = f"{BASE_URL}?{query}"

    def request() -> dict:
        try:
            with urlopen(url, timeout=10) as response:  # nosec B310 - fixed HTTPS provider URL
                return json.load(response)
        except OSError as exc:
            raise WeatherProviderError("Open-Meteo is unavailable; no weather observation was created.") from exc

    payload = await asyncio.to_thread(request)
    current = payload.get("current")
    if not current:
        reason = payload.get("reason", "current conditions were absent from the response")
        raise WeatherProviderError(f"Open-Meteo returned no current conditions: {reason}")

    return WeatherObservation(
        latitude=payload.get("latitude", latitude), longitude=payload.get("longitude", longitude),
        observed_at=current.get("time"), temperature_c=current.get("temperature_2m"),
        apparent_temperature_c=current.get("apparent_temperature"), precipitation_mm=current.get("precipitation"),
        weather_code=current.get("weather_code"), wind_speed_kmh=current.get("wind_speed_10m"),
        wind_gusts_kmh=current.get("wind_gusts_10m"), visibility_m=current.get("visibility"), source_url=url,
    )


def safety_risk(observation: WeatherObservation) -> tuple[bool, str, str]:
    """Classify a live observation with transparent travel-safety thresholds."""
    code = observation.weather_code
    if code in {95, 96, 99} or (observation.wind_gusts_kmh or 0) >= 70:
        return True, "CRITICAL", "thunderstorms or damaging wind gusts"
    if code in {48, 65, 66, 67, 75, 77, 81, 82, 86} or (observation.visibility_m is not None and observation.visibility_m < 1_000) or (observation.precipitation_mm or 0) >= 10:
        return True, "HIGH", "hazardous precipitation, fog, snow, or reduced visibility"
    if (observation.wind_gusts_kmh or 0) >= 50 or code in {45, 56, 57, 80, 85}:
        return True, "MEDIUM", "weather conditions requiring travel review"
    return False, "LOW", "no weather threshold exceeded"
