
import asyncio
import json
import os
import sys
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services import weather_client
from app.jobs import precompute
from app.models.model_server import ModelServer
from app.services.cache import CacheClient

async def verify():
    print("--- SolarSight Cross-Region Verification ---")
    
    # 1. Test Fallback Physics for specific regions
    print("\n[1] Testing Internal Fallback Physics (Seasonality Check)")
    cities_to_test = [
        {"name": "London", "lat": 51.5, "lon": 0.0},      # North Winter
        {"name": "Sydney", "lat": -33.8, "lon": 151.2},  # South Summer
        {"name": "Lagos", "lat": 6.5, "lon": 3.4}         # Tropics
    ]
    
    for city in cities_to_test:
        fb = weather_client.get_theoretical_fallback(city["lat"], city["lon"])
        rads = fb["hourly"]["shortwave_radiation"]
        peak = max(rads)
        # Find index of peak
        peak_idx = rads.index(peak)
        peak_time = fb["hourly"]["time"][peak_idx]
        
        # Count non-zero hours
        day_hours = len([r for r in rads[:24] if r > 0])
        
        print(f"📍 {city['name'].upper():<10} | Lat: {city['lat']:>5} | Peak: {peak:>6.1f} W/m2 | PeakTime: {peak_time} | Daylight: {day_hours} hrs")

    # 2. Check Live API Keys & Rotation
    print("\n[2] Checking API Keys configuration")
    keys = os.environ.get("OPEN_METEO_API_KEYS", "None")
    print(f"API Keys available: {'YES' if keys != 'None' else 'NO (Using Free Tier)'}")

    # 3. Cache Status
    print("\n[3] In-Memory Cache/Model Check")
    ms = ModelServer()
    print(f"Model Artifact Found: {'YES' if ms.model else 'NO (Will use heuristic with physical guardrails)'}")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(verify())
