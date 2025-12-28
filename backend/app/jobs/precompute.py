# backend/app/jobs/precompute.py
import os
import json
import asyncio
from typing import List, Dict, Any
from datetime import datetime
import numpy as np

from app.services import weather_client, feature_builder, co2, cache
from app.models.model_server import ModelServer

DEFAULT_CITIES = [
    {"name": "lagos", "lat": 6.5244, "lon": 3.3792},
    {"name": "nairobi", "lat": -1.286389, "lon": 36.817223},
    {"name": "cape_town", "lat": -33.9249, "lon": 18.4241},
    {"name": "london", "lat": 51.5074, "lon": -0.1278},
    {"name": "berlin", "lat": 52.52, "lon": 13.405},
    {"name": "paris", "lat": 48.8566, "lon": 2.3522},
    {"name": "tokyo", "lat": 35.6762, "lon": 139.6503},
    {"name": "new_york", "lat": 40.7128, "lon": -74.0060},
    {"name": "dubai", "lat": 25.2048, "lon": 55.2708},
    {"name": "sydney", "lat": -33.8688, "lon": 151.2093}
]

def load_cities() -> List[Dict[str, Any]]:
    raw = os.environ.get("CITY_LIST")
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list) and parsed:
                return parsed
        except Exception:
            pass
    return DEFAULT_CITIES

async def precompute_city(ms: ModelServer, cch: cache.CacheClient, city: Dict[str, Any], ttl: int) -> None:
    name = city["name"]
    lat = city["lat"]
    lon = city["lon"]
    try:
        fc_json = await weather_client.fetch_hourly_forecast(lat, lon, hours=48)
        feats_df = feature_builder.build_features(fc_json)
        pred = ms.predict_24h(feats_df)
        
        co2_per_hour = [float(co2.co2_avoided_kgs(float(k))) for k in pred.get("pred_kwh", [])]
        co2_total_24h = float(sum(co2_per_hour[:24]))
        
        # Explicit conversion to ensure NO non-serializable objects
        clean_hours = []
        for h in pred.get("hours", []):
            if hasattr(h, 'isoformat'):
                clean_hours.append(h.isoformat())
            else:
                clean_hours.append(str(h))

        payload = {
            "location": str(name),
            "generated_at_utc": datetime.utcnow().isoformat() + "Z",
            "timezone": fc_json.get("timezone", "UTC"),
            "timezone_abbr": fc_json.get("timezone_abbreviation", "UTC"),
            "hours": clean_hours,
            "pred_kwh": [float(x) for x in pred.get("pred_kwh", [])],
            "confidence": [float(x) for x in pred.get("confidence", [])],
            "co2_kg_per_hour": [float(x) for x in co2_per_hour],
            "co2_kg_total": float(co2_total_24h)
        }
        
        cch.set(name, payload, ttl=ttl)
        print(f"[{datetime.utcnow().isoformat()}] ✅ {name.upper()} | CO2: {co2_total_24h:.2f}kg")
    except Exception as e:
        print(f"[{datetime.utcnow().isoformat()}] ❌ {name}: {e}")
        # Log specific type info if it's a serialization error
        if "JSON" in str(e):
            try:
                print(f"DEBUG {name} hours[0] type: {type(pred.get('hours', [])[0])}")
            except: pass

async def run_precompute_cycle():
    cities = load_cities()
    ttl = int(os.environ.get("TTL_SECONDS", "3600")) # 1 hour default
    model_path = os.environ.get("MODEL_PATH", "./ml/artifacts/lightgbm_model.joblib")
    ms = ModelServer(model_path)
    cch = cache.CacheClient()
    semaphore = asyncio.Semaphore(3) # Reduce concurrency to avoid rate limits
    
    async def sem_task(city):
        async with semaphore:
            await precompute_city(ms, cch, city, ttl)
            
    tasks = [sem_task(city) for city in cities]
    await asyncio.gather(*tasks)

async def scheduler():
    while True:
        print(f"[{datetime.utcnow().isoformat()}] 🔄 Starting Precompute Cycle")
        await run_precompute_cycle()
        sleep_sec = 900
        print(f"[{datetime.utcnow().isoformat()}] ⏳ Sleeping {sleep_sec}s")
        await asyncio.sleep(sleep_sec)

if __name__ == "__main__":
    asyncio.run(scheduler())
