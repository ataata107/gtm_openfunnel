import time
import psutil
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from contextlib import asynccontextmanager

@dataclass
class PerformanceMetrics:
    start_time: float
    end_time: Optional[float] = None
    memory_usage_mb: float = 0
    cpu_usage_percent: float = 0
    api_calls: int = 0
    failed_requests: int = 0
    total_queries: int = 0
    processing_time_ms: Optional[float] = None
    
    def __post_init__(self):
        if self.end_time:
            self.processing_time_ms = (self.end_time - self.start_time) * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "processing_time_ms": self.processing_time_ms,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "api_calls": self.api_calls,
            "failed_requests": self.failed_requests,
            "total_queries": self.total_queries,
            "queries_per_second": self.total_queries / (self.processing_time_ms / 1000) if self.processing_time_ms else 0
        }

class PerformanceMonitor:
    def __init__(self):
        self.metrics = PerformanceMetrics(start_time=time.time())
        self.api_calls = 0
        self.failed_requests = 0
    
    def record_api_call(self):
        self.api_calls += 1
    
    def record_failed_request(self):
        self.failed_requests += 1
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=0.1)
    
    def finish(self, total_queries: int = 0) -> PerformanceMetrics:
        """Finish monitoring and return metrics"""
        self.metrics.end_time = time.time()
        self.metrics.memory_usage_mb = self.get_memory_usage()
        self.metrics.cpu_usage_percent = self.get_cpu_usage()
        self.metrics.api_calls = self.api_calls
        self.metrics.failed_requests = self.failed_requests
        self.metrics.total_queries = total_queries
        return self.metrics
    
    @asynccontextmanager
    async def monitor(self, operation_name: str = "operation"):
        """Context manager for monitoring operations"""
        start_time = time.time()
        initial_memory = self.get_memory_usage()
        
        try:
            yield self
        finally:
            end_time = time.time()
            final_memory = self.get_memory_usage()
            
            print(f"📊 Performance for {operation_name}:")
            print(f"   ⏱️  Time: {(end_time - start_time) * 1000:.2f}ms")
            print(f"   💾 Memory: {final_memory - initial_memory:.2f}MB")
            print(f"   📡 API Calls: {self.api_calls}")
            print(f"   ❌ Failed Requests: {self.failed_requests}")

# Global performance monitor
performance_monitor = PerformanceMonitor()

class OptimizedBatchProcessor:
    """Optimized batch processing with performance monitoring"""
    
    def __init__(self, batch_size: int = 50, max_concurrent: int = 20):
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
    
    async def process_batch(self, items: list, processor_func, monitor: PerformanceMonitor) -> list:
        """Process items in optimized batches"""
        results = []
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_item(item):
            async with semaphore:
                try:
                    result = await processor_func(item)
                    monitor.record_api_call()
                    return result
                except Exception as e:
                    monitor.record_failed_request()
                    print(f"❌ Failed to process item: {e}")
                    return None
        
        # Process in batches
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_results = await asyncio.gather(*[process_item(item) for item in batch])
            results.extend([r for r in batch_results if r is not None])
        
        return results

# Global optimized processor
optimized_processor = OptimizedBatchProcessor() 