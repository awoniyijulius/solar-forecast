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
    If not cached, return 503 to encourage precompute pattern.
    """
    cached = cache.get(location)
    if cached:
        return cached
    # fallback: rate-limited on-demand inference could be implemented here
    raise HTTPException(status_code=503, detail="Prediction not precomputed. Try again shortly.")
