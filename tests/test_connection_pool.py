import asyncio
import time
from utils.connection_pool import connection_pool, memory_processor
from utils.performance_monitor import performance_monitor

async def test_connection_pool_performance():
    """Test connection pooling performance"""
    
    print("🚀 Testing Connection Pool Performance...")
    
    # Test 1: Connection pool session management
    print("\n🔗 Test 1: Connection Pool Session Management")
    start_time = time.time()
    
    async with performance_monitor.monitor("connection_pool_test"):
        # Create multiple sessions to test pooling
        for i in range(10):
            async with connection_pool.get_session() as session:
                print(f"✅ Session {i+1} created successfully")
                await asyncio.sleep(0.01)  # Simulate work
    
    end_time = time.time()
    print(f"⏱️  Total time: {(end_time - start_time) * 1000:.2f}ms")
    
    # Test 2: Memory optimization
    print("\n💾 Test 2: Memory Optimization")
    test_items = list(range(500))
    
    async def process_batch(batch):
        # Simulate API processing
        await asyncio.sleep(0.01)
        return [item * 2 for item in batch]
    
    start_time = time.time()
    results = await memory_processor.process_large_dataset(test_items, process_batch)
    end_time = time.time()
    
    print(f"✅ Processed {len(results)} items")
    print(f"⏱️  Processing time: {(end_time - start_time) * 1000:.2f}ms")
    
    # Test 3: Deduplication
    print("\n🔄 Test 3: Deduplication")
    duplicate_items = [1, 2, 2, 3, 3, 3, 4, 5, 5]
    unique_items = memory_processor.deduplicate_results(duplicate_items)
    print(f"✅ Deduplicated {len(duplicate_items)} items to {len(unique_items)} unique items")
    
    print("\n🎉 Connection pool performance test completed!")

if __name__ == "__main__":
    asyncio.run(test_connection_pool_performance()) 