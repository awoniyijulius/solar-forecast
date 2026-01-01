from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services import weather_client, feature_builder, co2
from app.models.model_server import ModelServer
from app.services.cache import CacheClient

router = APIRouter()
model = ModelServer()
cache = CacheClient()

@router.get("/predictions/{location}")
async def get_predictions(location: str):
    """
    Return cached 24-hour hourly predictions for a location.
    If not cached, run on-demand inference (robust fallback).
    """
    # 1. Check Cache
    cached = cache.get(location)
    if cached:
        return cached

    # 2. On-Demand Calculation (Cache Miss)
    print(f"⚠️ Cache miss for {location}.running on-demand inference...")
    try:
        from app.jobs import precompute
        
        # Find city config
        cities = precompute.load_cities()
        city_config = next((c for c in cities if c["name"] == location), None)
        
        if not city_config:
             raise HTTPException(status_code=404, detail="City not supported")

        # Generate & Cache immediately
        payload = await precompute.generate_city_prediction(model, city_config)
        
        # Save to cache for next time
        cache.set(location, payload, ttl=3600)
        
        return payload
    except Exception as e:
        print(f"❌ On-demand inference failed: {e}")
        
        # Check if it's a rate limit error
        error_msg = str(e)
        status_code = 503
        
        if "429" in error_msg or "rate limit" in error_msg.lower():
            error_msg = "The weather data provider is temporarily busy. Please try again in 30 seconds."
            status_code = 429
            
        # fallback: return 503 or 429
        raise HTTPException(
            status_code=status_code, 
            detail=error_msg
        )
