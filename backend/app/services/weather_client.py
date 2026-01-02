import asyncio
import httpx
import random
import os
import datetime
from typing import Dict, Any
import logging
import math

logger = logging.getLogger(__name__)

# Base URLs
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
CUSTOMER_URL = "https://customer-api.open-meteo.com/v1/forecast"

class WeatherServiceError(Exception):
    """Custom exception for weather fetching failures"""
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def get_theoretical_fallback(lat: float, lon: float) -> Dict[str, Any]:
    """Generates a base 'clear-sky' fallback if the API is completely failing."""
    logger.warning(f"🛠️ Generating theoretical fallback for {lat}, {lon}")
    # Simple sine-wave based solar proxy
    hours = 72 # 3 days
    base_time = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    
    # Mock Open-Meteo structure
    return {
        "timezone": "UTC",
        "timezone_abbreviation": "UTC",
        "hourly": {
            "time": [(base_time + datetime.timedelta(hours=i)).isoformat() for i in range(hours)],
            "temperature_2m": [25.0 + 5.0 * math.sin((i+12) * math.pi/12) for i in range(hours)],
            "cloudcover": [10 for _ in range(hours)],
            "shortwave_radiation": [max(0, 800 * math.sin((i+6) * math.pi/12)) for i in range(hours)],
            "uv_index": [max(0, 8 * math.sin((i+6) * math.pi/12)) for i in range(hours)]
        },
        "is_fallback": True
    }

async def fetch_hourly_forecast(lat: float, lon: float, hours: int = 48) -> Dict[str, Any]:
    api_key = os.environ.get("OPEN_METEO_API_KEY")
    url = CUSTOMER_URL if api_key else OPEN_METEO_URL
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,cloudcover,shortwave_radiation,uv_index",
        "forecast_days": 3,
        "timezone": "auto"
    }
    if api_key:
        params["apikey"] = api_key
    
    max_retries = 3 # Reduced retries because we'll use fallback instead of hanging
    base_delay = 2
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
                r = await client.get(url, params=params)
                
                if r.status_code == 429:
                    wait_time = (base_delay ** attempt) + random.uniform(0, 1)
                    logger.warning(f"⚠️ Rate Limited. Retry {attempt+1}/{max_retries} in {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    continue
                
                r.raise_for_status()
                return r.json()
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"❌ Weather API failed permanently: {e}. Switching to fallback.")
                return get_theoretical_fallback(lat, lon)
            
            wait_time = (base_delay ** attempt) + random.uniform(0, 1)
            await asyncio.sleep(wait_time)
    
    return get_theoretical_fallback(lat, lon)
