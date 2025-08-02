import redis
import json
import hashlib
import os
from typing import Optional, Any, Dict, List
from dotenv import load_dotenv
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

class RedisCache:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
        self.default_ttl = 3600  # 1 hour default TTL
        
    def _generate_cache_key(self, prefix: str, data: Any) -> str:
        """Generate a consistent cache key from data"""
        data_str = json.dumps(data, sort_keys=True)
        hash_value = hashlib.md5(data_str.encode()).hexdigest()
        return f"{prefix}:{hash_value}"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with retry logic"""
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"⚠️ Cache get error for {key}: {e}")
            return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with retry logic"""
        try:
            ttl = ttl or self.default_ttl
            return self.redis_client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            print(f"⚠️ Cache set error for {key}: {e}")
            return False
    
    async def get_search_results(self, query: str, source: str) -> Optional[List[str]]:
        """Get cached search results for a query"""
        cache_key = self._generate_cache_key(f"search:{source}", {"query": query})
        return await self.get(cache_key)
    
    async def set_search_results(self, query: str, source: str, results: List[str], ttl: int = 7200) -> bool:
        """Cache search results for a query"""
        cache_key = self._generate_cache_key(f"search:{source}", {"query": query})
        return await self.set(cache_key, results, ttl)
    
    async def get_company_data(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get cached company data"""
        cache_key = f"company:{domain}"
        return await self.get(cache_key)
    
    async def set_company_data(self, domain: str, data: Dict[str, Any], ttl: int = 86400) -> bool:
        """Cache company data"""
        cache_key = f"company:{domain}"
        return await self.set(cache_key, data, ttl)
    
    async def get_llm_response(self, prompt: str, model: str) -> Optional[str]:
        """Get cached LLM response"""
        cache_key = self._generate_cache_key(f"llm:{model}", {"prompt": prompt})
        return await self.get(cache_key)
    
    async def set_llm_response(self, prompt: str, model: str, response: str, ttl: int = 3600) -> bool:
        """Cache LLM response"""
        cache_key = self._generate_cache_key(f"llm:{model}", {"prompt": prompt})
        return await self.set(cache_key, response, ttl)

# Global cache instance
cache = RedisCache()
