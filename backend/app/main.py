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
    
    # 2. Run initial precompute immediately (non-blocking if possible, but for v1 blocking is safer to ensure data exists)
    print("🔄 Running initial precompute job...")
    try:
        await precompute.run_precompute()
        print("✅ Initial precompute complete")
    except Exception as e:
        print(f"❌ Initial precompute failed: {e}")

    # 3. Start Background Loop for 15-min updates
    async def schedule_precompute():
        while True:
            await asyncio.sleep(900) # 15 minutes
            print("⏰ Triggering scheduled precompute...")
            try:
                await precompute.run_precompute()
            except Exception as e:
                print(f"❌ Scheduled precompute failed: {e}")

    asyncio.create_task(schedule_precompute())
    
    print("🚀 SolarSight Backend started successfully")
