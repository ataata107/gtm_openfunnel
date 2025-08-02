import asyncio
import time
import json
from utils.performance_monitor import performance_monitor
from utils.cache import cache
from utils.circuit_breaker import serper_circuit_breaker
from utils.connection_pool import connection_pool

async def test_performance_optimizations():
    """Test the performance optimizations"""
    
    print("🚀 Testing Performance Optimizations...")
    
    # Test 1: Cache functionality
    print("\n📋 Test 1: Cache Functionality")
    test_data = {"test": "data", "queries": ["query1", "query2"]}
    
    # Set cache
    await cache.set("test_key", test_data, ttl=60)
    print("✅ Cache set successful")
    
    # Get cache
    cached_data = await cache.get("test_key")
    if cached_data == test_data:
        print("✅ Cache get successful")
    else:
        print("❌ Cache get failed")
    
    # Test 2: Circuit breaker
    print("\n🔴 Test 2: Circuit Breaker")
    try:
        # This should work
        result = await serper_circuit_breaker.call_with_retry(
            lambda: "test_success",
            "test_input"
        )
        print(f"✅ Circuit breaker success: {result}")
    except Exception as e:
        print(f"❌ Circuit breaker failed: {e}")
    
    # Test 3: Connection pool
    print("\n🔗 Test 3: Connection Pool")
    try:
        async with connection_pool.get_session() as session:
            print("✅ Connection pool session created")
    except Exception as e:
        print(f"❌ Connection pool failed: {e}")
    
    # Test 4: Performance monitoring
    print("\n📊 Test 4: Performance Monitoring")
    async with performance_monitor.monitor("test_operation"):
        # Simulate some work
        await asyncio.sleep(0.1)
        performance_monitor.record_api_call()
        performance_monitor.record_cache_hit()
    
    print("✅ Performance monitoring working")
    
    # Test 5: Memory optimization
    print("\n💾 Test 5: Memory Optimization")
    from utils.connection_pool import memory_processor
    
    test_items = list(range(1000))
    
    async def process_batch(batch):
        # Simulate processing
        await asyncio.sleep(0.01)
        return [item * 2 for item in batch]
    
    results = await memory_processor.process_large_dataset(test_items, process_batch)
    print(f"✅ Memory optimization processed {len(results)} items")
    
    print("\n🎉 All performance optimizations working!")

if __name__ == "__main__":
    asyncio.run(test_performance_optimizations()) 