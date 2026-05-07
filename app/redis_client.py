import redis
import json
from typing import Optional,Any
from app.config import REDIS_URL

_redis_client = None
 
def get_redis():
  global _redis_client
  if _redis_client is None:
    if REDIS_URL:
      _redis_client = redis.from_url(
        REDIS_URL,
        decode_responses = True
      )
    else:
      return None
  return _redis_client

def cache_set(key:str, value:Any,ttl:int = 300)->bool:
  try:
    client = get_redis()
    if not client:
      return False
    client.setex(key,ttl,json.dumps(value))
    return True
  except Exception:
    return False

def cache_get(key:str)->Optional[Any]:
  try:
    client = get_redis()
    if not client:
      return None
    data = client.get(key)
    if data:
      return json.loads(data)
    return None
  except Exception:
    return None
  
def cache_delete(key:str)->bool:
  try:
    client = get_redis()
    if not client:
      return False
    client.delete(key)
    return True
  except Exception:
    return False

def cache_delete_pattern(pattern:str)->bool:
  try:
    client = get_redis()
    if not client:
      return False
    keys = client.keys(pattern)
    if keys:
      client.delete(*keys)
      return True
  except Exception:
    return False
  