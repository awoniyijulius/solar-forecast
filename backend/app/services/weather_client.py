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
            "temperature_2m": [25.0 + 5.0 * math.sin((i-6) * math.pi/12) for i in range(hours)],
            "cloudcover": [10 for _ in range(hours)],
            "shortwave_radiation": [max(0, 800 * math.sin((i-6) * math.pi/12)) for i in range(hours)],
            "uv_index": [max(0, 8 * math.sin((i-6) * math.pi/12)) for i in range(hours)]
        },
        "is_fallback": True
    }

async def fetch_hourly_forecast(lat: float, lon: float, hours: int = 48) -> Dict[str, Any]:
    # 1. Load and Shuffle Keys (Load Balancing)
    keys_str = os.environ.get("OPEN_METEO_API_KEYS")
    if keys_str:
        api_keys = [k.strip() for k in keys_str.split(",") if k.strip()]
    else:
        # Backwards compatibility
        single = os.environ.get("OPEN_METEO_API_KEY")
        api_keys = [single] if single else [None]
    
    # Randomize key order to distribute load if we verify keys logic
    # (Optional: keep sequential if you prefer primary/secondary)
    # random.shuffle(api_keys) 

    base_url = CUSTOMER_URL if any(api_keys) else OPEN_METEO_URL
    
    # Identify our app uniquely
    headers = {
        "User-Agent": "SolarSightForecastEngine/1.1 (https://solarsight.app)",
        "Accept": "application/json"
    }

    # 2. Key Rotation Loop
    for i, api_key in enumerate(api_keys):
        # Dynamically switch URL based on key presence (Customer vs Free API)
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
            
        try:
            async with httpx.AsyncClient(timeout=15.0, verify=False, headers=headers) as client:
                r = await client.get(url, params=params)
                
                if r.status_code == 429:
                    logger.warning(f"⚠️ Key {i+1}/{len(api_keys)} Saturated (429). Rotating to next key...")
                    continue # Try next key
                
                r.raise_for_status()
                return r.json() # Success!
                
        except Exception as e:
            logger.warning(f"⚠️ Key {i+1} Failed: {e}. Rotating...")
            continue
            
    # 3. Ultimate Fallback (If all keys fail)
    logger.error(f"❌ All {len(api_keys)} API keys failed for {lat},{lon}. Engaging Theoretical Physics Model.")
    return get_theoretical_fallback(lat, lon)
