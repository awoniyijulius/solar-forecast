from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api import predictions, admin
import os

app = FastAPI(
    title="SolarSight Intelligence Engine", 
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

@app.get("/", response_class=HTMLResponse)
async def root():
    from app.services.cache import CacheClient
    cache = CacheClient()
    hits = cache.get("system_impressions") or 0
    redis_status = "OPERATIONAL" if cache.redis_client else "LOCAL_MODE"
    
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>SolarSight API</title>
            <style>
                body {{ background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
                .card {{ background: rgba(255, 255, 255, 0.05); padding: 3rem; border-radius: 1.5rem; border: 1px solid rgba(255,255,255,0.1); text-align: center; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); backdrop-filter: blur(10px); }}
                h1 {{ margin: 0 0 1rem 0; font-weight: 800; font-size: 2.5rem; background: linear-gradient(to right, #4ade80, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
                .status {{ color: #4ade80; font-weight: bold; font-family: monospace; letter-spacing: 0.1em; }}
                .meta {{ color: #94a3b8; margin: 1.5rem 0; font-size: 0.9rem; }}
                a {{ background: rgba(255,255,255,0.1); color: #fff; text-decoration: none; padding: 0.75rem 1.5rem; border-radius: 0.75rem; display: inline-block; font-weight: 600; transition: all 0.2s; border: 1px solid rgba(255,255,255,0.1); }}
                a:hover {{ background: #fff; color: #000; transform: translateY(-2px); }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>SolarSight Intelligence Gateway</h1>
                <p>SYSTEM STATUS: <span class="status">● {redis_status}</span></p>
                <div class="meta">
                    <p>Version 1.2.0 • LightGBM Inference Engine</p>
                    <p>Total Impressions: {hits}</p>
                </div>
                <a href="/docs">🚀 Open Developer Console</a>
            </div>
        </body>
    </html>
    """

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
