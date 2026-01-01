import asyncio
import httpx
import random
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Minimal Open-Meteo client for hourly forecasts
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

class WeatherServiceError(Exception):
    """Custom exception for weather fetching failures"""
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

async def fetch_hourly_forecast(lat: float, lon: float, hours: int = 48) -> Dict[str, Any]:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,cloudcover,shortwave_radiation,uv_index",
        "forecast_days": 3,
        "timezone": "auto"
    }
    
    max_retries = 5
    base_delay = 2
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
                r = await client.get(OPEN_METEO_URL, params=params)
                
                if r.status_code == 429:
                    # Exponential backoff with jitter
                    wait_time = (base_delay ** attempt) + random.uniform(0, 1)
                    logger.warning(f"⚠️ Open-Meteo Rate Limit (429). Retrying in {wait_time:.2f}s... (Attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
                
                r.raise_for_status()
                return r.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                wait_time = (base_delay ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(wait_time)
                continue
            
            if attempt == max_retries - 1:
                raise WeatherServiceError(f"Weather API returned {e.response.status_code}", status_code=e.response.status_code)
            
        except Exception as e:
            if attempt == max_retries - 1:
                raise WeatherServiceError(f"Unexpected error fetching weather: {str(e)}")
            
            wait_time = (base_delay ** attempt) + random.uniform(0, 1)
            logger.warning(f"⚠️ Weather fetch attempt {attempt+1} failed: {e}. Retrying in {wait_time:.2f}s...")
            await asyncio.sleep(wait_time)
    
    raise WeatherServiceError("Failed to fetch weather data after max retries", status_code=429)
