from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services import weather_client, feature_builder, co2
from app.models.model_server import ModelServer
from app.services.cache import CacheClient

router = APIRouter()
model = ModelServer()
cache = CacheClient()

# In-memory locks to prevent multiple simultaneous fetches for the same city (Request Collapsing)
locks: Dict[str, asyncio.Lock] = {}

@router.get("/predictions/{location}")
async def get_predictions(location: str):
    """
    Return cached 24-hour hourly predictions for a location.
    If not cached, run on-demand inference with a lock to prevent duplicate hits.
    """
    # 1. Check Cache first (Fast Path)
    cached = cache.get(location)
    if cached:
        return cached

    # 2. Get or create a lock for this specific location
    if location not in locks:
        locks[location] = asyncio.Lock()
    
    async with locks[location]:
        # Double-check cache inside the lock (in case another thread just filled it)
        cached_again = cache.get(location)
        if cached_again:
            return cached_again

        # 3. On-Demand Calculation (Cache Miss)
        print(f"⚠️ Cache miss for {location}. Running on-demand inference with Single-Flight lock...")
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
            print(f"❌ On-demand inference failed for {location}: {e}")
            
            # Check if it's a rate limit error
            error_msg = str(e)
            status_code = 503
            
            if "429" in error_msg or "rate limit" in error_msg.lower():
                error_msg = "The weather data provider is temporarily busy. Please try again in 30 seconds."
                status_code = 429
                
            raise HTTPException(status_code=status_code, detail=error_msg)
