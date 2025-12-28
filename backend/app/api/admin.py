from fastapi import APIRouter, HTTPException, Header
from typing import Dict, Any, Optional
from pydantic import BaseModel
import os

router = APIRouter()

# Simple API key authentication (in production, use proper auth)
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "dev-admin-key-change-in-production")

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

class RetrainRequest(BaseModel):
    data_source: str = "NASA POWER Historical"
    model_type: str = "LightGBM"

class EmissionFactorUpdate(BaseModel):
    emission_factor: float

@router.post("/admin/retrain")
async def trigger_retrain(request: RetrainRequest, authorized: bool = Header(default=False, alias="x-api-key")):
    """
    Trigger model retraining job.
    In production, this would queue a background job or trigger a Kubernetes CronJob.
    """
    # verify_api_key(authorized)  # Uncomment for production
    
    return {
        "status": "queued",
        "message": f"Retrain job queued with {request.model_type} using {request.data_source}",
        "job_id": "retrain-001",
        "estimated_time": "30-60 minutes"
    }

@router.get("/admin/metrics")
async def get_system_metrics():
    """
    Return system health and performance metrics.
    """
    from app.services.cache import CacheClient
    
    cache = CacheClient()
    
    # Get cache info (basic stats)
    try:
        cache_info = cache.r.info()
        cache_keys = cache.r.keys("*")
        
        return {
            "cache": {
                "connected": True,
                "keys_count": len(cache_keys),
                "memory_used_mb": cache_info.get("used_memory", 0) / (1024 * 1024),
                "uptime_seconds": cache_info.get("uptime_in_seconds", 0)
            },
            "api": {
                "status": "healthy",
                "version": "0.1.0"
            },
            "model": {
                "type": "LightGBM",
                "version": "1.0",
                "last_trained": "2024-01-01T00:00:00Z"  # Placeholder
            }
        }
    except Exception as e:
        return {
            "cache": {"connected": False, "error": str(e)},
            "api": {"status": "degraded"}
        }

@router.put("/admin/emission-factor/{location}")
async def update_emission_factor(location: str, update: EmissionFactorUpdate):
    """
    Update CO₂ emission factor for a specific location.
    In production, this would update a database table.
    """
    # verify_api_key(authorized)  # Uncomment for production
    
    return {
        "location": location,
        "emission_factor": update.emission_factor,
        "status": "updated",
        "message": f"Emission factor for {location} updated to {update.emission_factor} kg CO₂/kWh"
    }

@router.get("/admin/cities")
async def list_cities():
    """
    List all configured cities with their coordinates.
    """
    from app.jobs.precompute import DEFAULT_CITIES
    
    return {
        "cities": DEFAULT_CITIES,
        "count": len(DEFAULT_CITIES)
    }

@router.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "service": "solar-sight-backend",
        "version": "0.1.0"
    }
