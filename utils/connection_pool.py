import aiohttp
import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import gc
import atexit

class ConnectionPool:
    def __init__(self, 
                 max_connections: int = 100,
                 max_connections_per_host: int = 20,
                 timeout: int = 30):
        self.max_connections = max_connections
        self.max_connections_per_host = max_connections_per_host
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
        self._connector: Optional[aiohttp.TCPConnector] = None
        
        # Register cleanup on exit
        atexit.register(self._cleanup_sync)
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with connection pooling"""
        if self._session is None or self._session.closed:
            self._connector = aiohttp.TCPConnector(
                limit=self.max_connections,
                limit_per_host=self.max_connections_per_host,
                keepalive_timeout=60,
                enable_cleanup_closed=True
            )
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                connector=self._connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'GTM-Research-Engine/1.0'
                }
            )
        
        return self._session
    
    @asynccontextmanager
    async def get_session(self):
        """Context manager for getting session"""
        session = await self._get_session()
        try:
            yield session
        except Exception as e:
            print(f"⚠️ Session error: {e}")
            raise
    
    async def close(self):
        """Close the session and connector"""
        if self._session and not self._session.closed:
            await self._session.close()
        if self._connector and not self._connector.closed:
            await self._connector.close()
    
    def _cleanup_sync(self):
        """Synchronous cleanup for atexit"""
        try:
            # Create a new event loop if none exists
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            if not loop.is_closed():
                loop.run_until_complete(self.close())
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
    
    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make GET request with connection pooling"""
        async with self.get_session() as session:
            return await session.get(url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make POST request with connection pooling"""
        async with self.get_session() as session:
            return await session.post(url, **kwargs)

# Global connection pool
connection_pool = ConnectionPool()

class MemoryOptimizedProcessor:
    """Memory-efficient processing for large datasets"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
    
    async def process_large_dataset(self, items: list, processor_func) -> list:
        """Process large datasets in batches to manage memory"""
        results = []
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_results = await processor_func(batch)
            results.extend(batch_results)
            
            # Force garbage collection after each batch
            import gc
            gc.collect()
        
        return results
    
    def deduplicate_results(self, results: list, key_func=None) -> list:
        """Deduplicate results efficiently"""
        seen = set()
        unique_results = []
        
        for item in results:
            key = key_func(item) if key_func else str(item)
            if key not in seen:
                seen.add(key)
                unique_results.append(item)
        
        return unique_results

# Global memory processor
memory_processor = MemoryOptimizedProcessor() 