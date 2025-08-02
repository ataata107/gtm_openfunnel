#!/usr/bin/env python3
"""
Simple test to measure GPT-4o response time with a sample query.
"""

import time
import sys
import os
import asyncio

# Add the parent directory to the path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

async def test_gpt4o_async():
    """Test GPT-4o with async calls"""
    
    print("🧪 Testing GPT-4o Async Query Performance")
    print("=" * 50)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found")
        return
    
    # Create LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Simple query
    simple_query = "What are 3 fintech companies that use AI for fraud detection?"
    
    print(f"📝 Query: {simple_query}")
    print("\n⏱️  Testing single call...")
    
    # Test single call
    start_time = time.time()
    
    try:
        response = await llm.ainvoke(simple_query)
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        print(f"✅ Single async call took: {duration_ms:.2f}ms ({duration_ms/1000:.2f}s)")
        print(f"📊 Response length: {len(response.content)} characters")
        print(f"\n📝 Response preview:")
        print(response.content[:200] + "..." if len(response.content) > 200 else response.content)
        
        # Test multiple async calls
        print(f"\n⏱️  Testing 5 async calls in parallel...")
        start_time = time.time()
        
        async def make_call(call_num):
            call_start = time.time()
            response = await llm.ainvoke(simple_query)
            call_end = time.time()
            call_duration = (call_end - call_start) * 1000
            print(f"  Call {call_num}: {call_duration:.2f}ms")
            return call_duration
        
        # Run all calls in parallel
        tasks = [make_call(i+1) for i in range(5)]
        call_durations = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_duration_ms = (end_time - start_time) * 1000
        avg_duration_ms = sum(call_durations) / len(call_durations)
        
        print(f"\n📊 Results:")
        print(f"  Total time for 5 async calls: {total_duration_ms:.2f}ms")
        print(f"  Average per call: {avg_duration_ms:.2f}ms")
        print(f"  Calls per second: {1000/avg_duration_ms:.2f}")
        print(f"  Parallel speedup: {total_duration_ms/avg_duration_ms:.1f}x")
        
        return {
            "single_call_ms": duration_ms,
            "five_calls_ms": total_duration_ms,
            "avg_call_ms": avg_duration_ms,
            "calls_per_second": 1000/avg_duration_ms,
            "parallel_speedup": total_duration_ms/avg_duration_ms
        }
        
    except Exception as e:
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        print(f"❌ Test failed after {duration_ms:.2f}ms: {e}")
        return None

def test_gpt4o_simple():
    """Test GPT-4o with a simple query and measure response time"""
    
    print("🧪 Testing GPT-4o Simple Query Performance")
    print("=" * 50)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found")
        return
    
    # Create LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Simple query
    simple_query = "What are 3 fintech companies that use AI for fraud detection?"
    
    print(f"📝 Query: {simple_query}")
    print("\n⏱️  Testing response time...")
    
    # Test single call
    start_time = time.time()
    
    try:
        response = llm.invoke(simple_query)
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        print(f"✅ Single call took: {duration_ms:.2f}ms ({duration_ms/1000:.2f}s)")
        print(f"📊 Response length: {len(response.content)} characters")
        print(f"\n📝 Response preview:")
        print(response.content[:200] + "..." if len(response.content) > 200 else response.content)
        
        # Test multiple calls
        print(f"\n⏱️  Testing 5 sequential calls...")
        start_time = time.time()
        
        for i in range(5):
            call_start = time.time()
            response = llm.invoke(simple_query)
            call_end = time.time()
            call_duration = (call_end - call_start) * 1000
            print(f"  Call {i+1}: {call_duration:.2f}ms")
        
        end_time = time.time()
        total_duration_ms = (end_time - start_time) * 1000
        avg_duration_ms = total_duration_ms / 5
        
        print(f"\n📊 Results:")
        print(f"  Total time for 5 calls: {total_duration_ms:.2f}ms")
        print(f"  Average per call: {avg_duration_ms:.2f}ms")
        print(f"  Calls per second: {1000/avg_duration_ms:.2f}")
        
        return {
            "single_call_ms": duration_ms,
            "five_calls_ms": total_duration_ms,
            "avg_call_ms": avg_duration_ms,
            "calls_per_second": 1000/avg_duration_ms
        }
        
    except Exception as e:
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        print(f"❌ Test failed after {duration_ms:.2f}ms: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Testing both sequential and async approaches...")
    print("=" * 60)
    
    # Test sequential first
    print("\n📊 SEQUENTIAL TEST:")
    sequential_results = test_gpt4o_simple()
    
    # Test async
    print("\n📊 ASYNC TEST:")
    async_results = asyncio.run(test_gpt4o_async())
    
    # Compare results
    if sequential_results and async_results:
        print("\n📊 COMPARISON:")
        print("=" * 30)
        print(f"Sequential 5 calls: {sequential_results['five_calls_ms']:.2f}ms")
        print(f"Async 5 calls:      {async_results['five_calls_ms']:.2f}ms")
        
        speedup = sequential_results['five_calls_ms'] / async_results['five_calls_ms']
        print(f"Async speedup:      {speedup:.1f}x faster")
        
        print(f"\nSequential avg:     {sequential_results['avg_call_ms']:.2f}ms per call")
        print(f"Async avg:          {async_results['avg_call_ms']:.2f}ms per call") 