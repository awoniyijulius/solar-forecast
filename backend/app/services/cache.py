import redis
import json
import os
from datetime import datetime
import numpy as np
import logging
from diskcache import Cache

REDIS_URL = os.environ.get("REDIS_URL", "")

logger = logging.getLogger(__name__)

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(CustomEncoder, self).default(obj)

class CacheClient:
    def __init__(self):
        self.redis_client = None
        self.disk_cache = None
        
        if REDIS_URL:
            try:
                self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                logger.info("✅ Connected to Redis")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed: {e}. Falling back to DiskCache.")
                self.redis_client = None
        
        if not self.redis_client:
            logger.info("📂 Using local file-based cache (DiskCache)")
            self.disk_cache = Cache("local_cache_data")

    def get(self, key: str):
        if self.redis_client:
            v = self.redis_client.get(key)
            if v:
                try:
                    return json.loads(v)
                except Exception:
                    return v
            return None
        
        # DiskCache fallback
        return self.disk_cache.get(key)

    def set(self, key: str, value, ttl: int = 3600):
        # Use our custom encoder
        # For DiskCache, strictly we don't need to JSON stringify, but for consistency we do
        # so objects are returned as dicts/primitives
        json_val = json.loads(json.dumps(value, cls=CustomEncoder))
        
        if self.redis_client:
            str_val = json.dumps(json_val) # Redis needs string
            self.redis_client.set(key, str_val, ex=ttl)
        else:
            self.disk_cache.set(key, json_val, expire=ttl)
