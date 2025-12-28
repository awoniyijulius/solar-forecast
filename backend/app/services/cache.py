import redis
import json
import os
from datetime import datetime
import numpy as np

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

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
        # We use decode_responses=True safely because we only store JSON strings
        self.r = redis.from_url(REDIS_URL, decode_responses=True)

    def get(self, key: str):
        v = self.r.get(key)
        if v:
            try:
                return json.loads(v)
            except Exception:
                return v
        return None

    def set(self, key: str, value, ttl: int = 3600):
        # Use our custom encoder to handle Timestamps or Numpy types automatically
        json_val = json.dumps(value, cls=CustomEncoder)
        self.r.set(key, json_val, ex=ttl)
