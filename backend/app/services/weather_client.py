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
    
    hours = 72 # 3 days
    base_time_utc = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    
    # Estimate local time offset from UTC (15 degrees per hour)
    offset_hours = round(lon / 15.0)
    
    times = []
    temps = []
    clouds = []
    rads = []
    uvs = []
    
    for i in range(hours):
        # We need to generate LOCAL time strings because that's what the ML model (feature_builder) expects
        # (It extracts .dt.hour from the string). 
        # If we send UTC 02:00 for Sydney, Model sees hour=2 (Night).
        # We want Model to see hour=12 (Noon).
        # So we construct the Local Datetime.
        
        utc_point = base_time_utc + datetime.timedelta(hours=i)
        local_point = utc_point + datetime.timedelta(hours=offset_hours)
        
        times.append(local_point.isoformat())
        
        # Calculate solar position based on this Local Hour
        local_hour = local_point.hour + (local_point.minute / 60.0)
        
        # Solar estimation: Sun roughly up between 6:00 and 18:00 Local Time
        # Peak at 12:00
        if 6.0 <= local_hour <= 18.0:
            # Sine wave from 0 to pi
            # (local_hour - 6) maps 6->0, 12->6, 18->12. Divide by 12 * pi
            factor = math.sin((local_hour - 6.0) / 12.0 * math.pi)
            factor = max(0.0, factor)
        else:
            factor = 0.0
            
        # Generate synthetic data
        rad = 1000.0 * factor  # Max 1000 W/m2
        uv = 11.0 * factor     # Max UV 11
        temp = 20.0 + (10.0 * factor) # 20C night, 30C day
        
        rads.append(round(rad, 1))
        uvs.append(round(uv, 1))
        temps.append(round(temp, 1))
        clouds.append(0) # Clear sky assumption for fallback
        
    # Construct a GMT offset string (e.g., "GMT+9")
    sign = "+" if offset_hours >= 0 else ""
    tz_str = f"GMT{sign}{offset_hours}"

    return {
        "timezone": tz_str,
        "timezone_abbreviation": tz_str,
        "hourly": {
            "time": times,
            "temperature_2m": temps,
            "cloudcover": clouds,
            "shortwave_radiation": rads,
            "uv_index": uvs
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
