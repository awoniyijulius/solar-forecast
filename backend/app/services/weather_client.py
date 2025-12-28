import httpx
from typing import Dict, Any
import datetime

# Minimal Open-Meteo client for hourly forecasts
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

async def fetch_hourly_forecast(lat: float, lon: float, hours: int = 48) -> Dict[str, Any]:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,cloudcover,shortwave_radiation,uv_index",
        "forecast_days": 3,
        "timezone": "auto"
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(OPEN_METEO_URL, params=params)
        r.raise_for_status()
        return r.json()
