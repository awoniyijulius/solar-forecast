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
    from app.services.cache import CacheClient
    cache = CacheClient()
    hits = cache.get("system_impressions") or 0
    return {
        "service": "solar-sight-backend",
        "status": "ok",
        "total_impressions": hits,
        "version": "1.1.0"
    }

@app.post("/api/analytics/hit")
async def track_impression():
    from app.services.cache import CacheClient
    cache = CacheClient()
    current = cache.get("system_impressions") or 0
    new_total = current + 1
    cache.set("system_impressions", new_total, ttl=None) # Persistent
    return {"status": "recorded", "count": new_total}

@app.get("/api/health")
async def health_check():
    """Diagnostic health check for system status"""
    from app.services.cache import CacheClient
    cache = CacheClient()
    
    # Check Redis
    redis_status = "connected" if cache.redis_client else "local_fallback"
    
    return {
        "status": "operational",
        "components": {
            "api": "healthy",
            "database": redis_status,
            "ml_engine": "loaded"
        },
        "version": "1.2.0"
    }

@app.on_event("startup")
async def startup_event():
    """Verify connections on startup and start background scheduler"""
    from app.services.cache import CacheClient
    from app.jobs import precompute
    import asyncio
    
    # 1. Initialize Cache
    try:
        cache = CacheClient()
        if cache.redis_client:
             print("✅ Redis connection successful")
        else:
             print("📂 DiskCache initialized (Redis unavailable)")
    except Exception as e:
        print(f"⚠️ Cache init warning: {e}")
    
    # 2. Start Background Loop (Immediate + Scheduled)
    async def run_scheduler():
        # Delay slightly to let server start serving requests
        await asyncio.sleep(5)
        print("🔄 Running initial precompute job (Background)...")
        try:
            await precompute.run_precompute()
            print("✅ Initial precompute complete")
        except Exception as e:
             print(f"❌ Initial precompute failed: {e}")

        while True:
            await asyncio.sleep(900) # 15 minutes
            print("⏰ Triggering scheduled precompute...")
            try:
                await precompute.run_precompute()
            except Exception as e:
                print(f"❌ Scheduled precompute failed: {e}")

    asyncio.create_task(run_scheduler())
    
    print("🚀 SolarSight Backend started successfully")
