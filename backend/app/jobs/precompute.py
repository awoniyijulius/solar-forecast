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

async def generate_city_prediction(ms: ModelServer, city: Dict[str, Any]) -> Dict[str, Any]:
    name = city["name"]
    lat = city["lat"]
    lon = city["lon"]
    
    fc_json = await weather_client.fetch_hourly_forecast(lat, lon, hours=48)
    feats_df = feature_builder.build_features(fc_json)
    pred = ms.predict_24h(feats_df)
    
    # NEW: Using regional intensity factors for climate impact accuracy
    co2_per_hour = [float(co2.co2_avoided_kgs(float(k), name)) for k in pred.get("pred_kwh", [])]
    co2_total_24h = float(sum(co2_per_hour[:24]))
    
    # Explicit conversion to ensure NO non-serializable objects
    clean_hours = []
    for h in pred.get("hours", []):
        if hasattr(h, 'isoformat'):
            clean_hours.append(h.isoformat())
        else:
            clean_hours.append(str(h))

    # --- NEW: UV Health & Agricultural Metrics ---
    hourly = fc_json.get("hourly", {})
    uv_data = hourly.get("uv_index", [0] * 48)
    cloud_data = hourly.get("cloudcover", [50] * 48)
    temp_data = hourly.get("temperature_2m", [25] * 48)
    radiation_data = hourly.get("shortwave_radiation", [0] * 48)
    
    # Peak UV calculation (first 24 hours)
    uv_24h = uv_data[:24] if len(uv_data) >= 24 else uv_data
    peak_uv = max(uv_24h) if uv_24h else 0
    peak_uv_hour = uv_24h.index(peak_uv) if uv_24h and peak_uv > 0 else 12
    
    # UV Risk Classification (WHO Standard)
    if peak_uv >= 11:
        uv_risk = "Extreme"
        safe_exposure_mins = 10
    elif peak_uv >= 8:
        uv_risk = "Very High"
        safe_exposure_mins = 15
    elif peak_uv >= 6:
        uv_risk = "High"
        safe_exposure_mins = 25
    elif peak_uv >= 3:
        uv_risk = "Moderate"
        safe_exposure_mins = 45
    else:
        uv_risk = "Low"
        safe_exposure_mins = 60
    
    # Agricultural Advisory: Find best crop-drying windows (high radiation, low cloud)
    drying_windows = []
    for i in range(min(24, len(radiation_data))):
        rad = radiation_data[i] if i < len(radiation_data) else 0
        cloud = cloud_data[i] if i < len(cloud_data) else 50
        if rad > 400 and cloud < 30:
            drying_windows.append(i)
    
    # Irrigation advisory: high temp + high UV = water in evening
    avg_temp = sum(temp_data[:12]) / 12 if len(temp_data) >= 12 else 25
    irrigation_advice = "Evening (after 17:00)" if avg_temp > 28 and peak_uv > 6 else "Morning (06:00-09:00)"

    payload = {
        "location": str(name),
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "timezone": fc_json.get("timezone", "UTC"),
        "timezone_abbr": fc_json.get("timezone_abbreviation", "UTC"),
        "hours": clean_hours,
        "pred_kwh": [float(x) for x in pred.get("pred_kwh", [])],
        "confidence": [float(x) for x in pred.get("confidence", [])],
        "co2_kg_per_hour": [float(x) for x in co2_per_hour],
        "co2_kg_total": float(co2_total_24h),
        # NEW: Health & Agri Data
        "uv_index": [float(x) for x in uv_24h],
        "peak_uv": float(peak_uv),
        "peak_uv_hour": int(peak_uv_hour),
        "uv_risk_level": uv_risk,
        "safe_sun_exposure_mins": int(safe_exposure_mins),
        "agri_drying_windows": drying_windows,
        "agri_irrigation_advice": irrigation_advice
    }
    return payload

async def precompute_city(ms: ModelServer, cch: cache.CacheClient, city: Dict[str, Any], ttl: int) -> None:
    name = city["name"]
    try:
        # 🛡️ DEBOUNCER: Avoid hitting API if we already have fresh data (< 12 mins old)
        # This prevents redundant hits when the app restarts/redeploys
        existing = cch.get(name)
        if existing and "generated_at_utc" in existing:
            try:
                # Remove Z and handle ISO format
                ts = existing["generated_at_utc"].replace("Z", "")
                last_gen = datetime.fromisoformat(ts)
                age_sec = (datetime.utcnow() - last_gen).total_seconds()
                
                if age_sec < 720: # 12 minutes
                    print(f"[{datetime.utcnow().isoformat()}] ⏩ {name.upper()} | Cache is fresh ({age_sec:.0f}s old). Skipping API hit.")
                    return
            except Exception:
                pass # If parsing fails, proceed to refresh

        payload = await generate_city_prediction(ms, city)
        cch.set(name, payload, ttl=ttl)
        print(f"[{datetime.utcnow().isoformat()}] ✅ {name.upper()} | CO2: {payload['co2_kg_total']:.2f}kg")
    except Exception as e:
        print(f"[{datetime.utcnow().isoformat()}] ❌ {name}: {e}")

async def run_precompute_cycle():
    cities = load_cities()
    ttl = int(os.environ.get("TTL_SECONDS", "3600")) # 1 hour default
    model_path = os.environ.get("MODEL_PATH", "./ml/artifacts/lightgbm_model.joblib")
    ms = ModelServer(model_path)
    cch = cache.CacheClient()
    
    # Process cities one by one to avoid triggering rate limits on the free tier
    print(f"🔄 Starting sequential precompute for {len(cities)} cities...")
    for city in cities:
        await precompute_city(ms, cch, city, ttl)
        # Add a small delay between cities to be ultra-safe
        await asyncio.sleep(2)
    
    print("✅ All cities precomputed.")

async def scheduler():
    while True:
        print(f"[{datetime.utcnow().isoformat()}] 🔄 Starting Precompute Cycle")
        await run_precompute_cycle()
        sleep_sec = 900
        print(f"[{datetime.utcnow().isoformat()}] ⏳ Sleeping {sleep_sec}s")
        await asyncio.sleep(sleep_sec)


# Alias for external import
run_precompute = run_precompute_cycle

if __name__ == "__main__":
    asyncio.run(scheduler())
