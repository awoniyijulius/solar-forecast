from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import predictions, admin
import os

app = FastAPI(
    title="SolarSight Backend", 
    version="0.1.0",
    description="Real-time solar energy prediction API with 24-hour forecasts and CO₂ tracking"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predictions.router, prefix="/api", tags=["Predictions"])
app.include_router(admin.router, tags=["Admin"])

@app.get("/")
async def root():
    return {
        "service": "solar-sight-backend",
        "status": "ok",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.on_event("startup")
async def startup_event():
    """Verify connections on startup"""
    from app.services.cache import CacheClient
    
    try:
        cache = CacheClient()
        cache.r.ping()
        print("✅ Redis connection successful")
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}")
    
    print("🚀 SolarSight Backend started successfully")
