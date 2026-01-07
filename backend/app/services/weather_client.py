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
    """Generates a base 'clear-sky' fallback locally aligned from Midnight to Midnight."""
    logger.warning(f"🛠️ Generating aligned theoretical fallback for {lat}, {lon}")
    
    hours = 72 # 3 days
    
    # Estimate local time offset
    offset_hours = round(lon / 15.0)
    
    # Calculate "Local Midnight" anchor
    # We take current UTC, add offset to get "Local Now", then snap to hour=0
    utc_now = datetime.datetime.utcnow()
    local_now = utc_now + datetime.timedelta(hours=offset_hours)
    local_midnight = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Determine Seasonality / Intensity based on Latitude & Month (Jan)
    month = datetime.datetime.utcnow().month
    
    # Simple heuristic for Jan/Dec (Northern Winter, Southern Summer)
    is_winter_north = (month >= 11 or month <= 2)
    
    # Defaults (Tropics/Fall/Spring) - Equinox-ish
    peak_intensity = 900.0
    day_start = 6.5
    day_end = 17.5
    
    if is_winter_north:
        if lat > 30: # Northern Winter (e.g. London, Berlin, NYC)
            peak_intensity = 350.0 # Low intensity
            day_start = 8.5        # Short day
            day_end = 16.0
        elif lat < -30: # Southern Summer (e.g. Sydney, Cape Town)
            peak_intensity = 1100.0 # High intensity
            day_start = 5.5         # Long day
            day_end = 20.0
        # Else Tropics (Lagos, Nairobi): Keep Defaults
    
    times = []
    temps = []
    
    # Arrays
    clouds = []
    rads = []
    uvs = []
    
    for i in range(hours):
        # Generate timestamps starting from LOCAL MIDNIGHT
        future_local = local_midnight + datetime.timedelta(hours=i)
        times.append(future_local.isoformat())
        
        # Local hour is just 'i modulo 24'
        local_hour = i % 24
        
        # Solar estimation with dynamic day length
        if day_start <= local_hour <= day_end:
            # Normalize hour to 0..1 range within the window
            window_len = day_end - day_start
            pos = (local_hour - day_start) / window_len
            # Sine wave (0 to pi)
            factor = math.sin(pos * math.pi)
            factor = max(0.0, factor)
        else:
            factor = 0.0
            
        # Generate synthetic data with dynamic peak
        rad = peak_intensity * factor
        # UV is roughly proportional to Rad (1000W/m2 ~= 11 UV)
        uv = (peak_intensity / 90.0) * factor 
        
        # Temp lags sun, but simple approximation: Min 15C, Max is base + effect
        base_temp = 25.0 if lat < 30 and lat > -30 else (5.0 if lat > 30 else 20.0)
        temp = base_temp + (10.0 * factor) 
        
        rads.append(round(rad, 1))
        uvs.append(round(uv, 1))
        temps.append(round(temp, 1))
        clouds.append(10) # Slight cloud for realism 
        
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
