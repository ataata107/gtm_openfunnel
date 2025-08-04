#!/usr/bin/env python3
"""
Performance test for query agent
"""

import time
from agents.query_agent import query_agent
from graph.state import GTMState

def test_query_agent_performance():
    """Test query agent performance with different search depths"""
    
    test_cases = [
        {
            "name": "Quick Search",
            "research_goal": "Find fintech companies using AI for fraud detection",
            "search_depth": "quick",
            "expected_strategies": 8
        },
        {
            "name": "Standard Search", 
            "research_goal": "Find B2B SaaS companies with 50-200 employees raising Series A in 2024",
            "search_depth": "standard",
            "expected_strategies": 15
        },
        {
            "name": "Comprehensive Search",
            "research_goal": "Find companies using Kubernetes in production with recent security incidents",
            "search_depth": "comprehensive", 
            "expected_strategies": 25
        }
    ]
    
    print("🧪 QUERY AGENT PERFORMANCE TEST")
    print("=" * 50)
    
    total_time = 0
    total_strategies = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print(f"🎯 Research Goal: {test_case['research_goal']}")
        print(f"🔍 Search Depth: {test_case['search_depth']}")
        print(f"📊 Expected Strategies: {test_case['expected_strategies']}")
        
        # Create test state
        state = GTMState(
            research_goal=test_case['research_goal'],
            search_depth=test_case['search_depth'],
            max_parallel_searches=20,
            confidence_threshold=0.8,
            max_iterations=1
        )
        
        # Measure execution time
        start_time = time.time()
        result = query_agent(state)
        end_time = time.time()
        
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        strategies_generated = len(result.search_strategies_generated)
        
        print(f"⏱️  Execution Time: {execution_time:.2f}ms ({execution_time/1000:.2f}s)")
        print(f"📊 Strategies Generated: {strategies_generated}")
        print(f"✅ Success: {'Yes' if strategies_generated > 0 else 'No'}")
        
        # Show first few strategies
        if strategies_generated > 0:
            print("📝 Sample Strategies:")
            for j, strategy in enumerate(result.search_strategies_generated[:3], 1):
                print(f"   {j}. {strategy}")
            if strategies_generated > 3:
                print(f"   ... and {strategies_generated - 3} more")
        
        total_time += execution_time
        total_strategies += strategies_generated
        
        print("-" * 50)
    
    # Summary
    print("\n📊 PERFORMANCE SUMMARY")
    print("=" * 30)
    print(f"⏱️  Total Execution Time: {total_time:.2f}ms ({total_time/1000:.2f}s)")
    print(f"📊 Total Strategies Generated: {total_strategies}")
    print(f"📈 Average Time per Strategy: {total_time/total_strategies:.2f}ms" if total_strategies > 0 else "📈 No strategies generated")
    print(f"🚀 Average Time per Test: {total_time/len(test_cases):.2f}ms")
    
    # Performance rating
    avg_time_per_test = total_time / len(test_cases)
    if avg_time_per_test < 2000:  # Less than 2 seconds
        rating = "🚀 EXCELLENT"
    elif avg_time_per_test < 5000:  # Less than 5 seconds
        rating = "✅ GOOD"
    elif avg_time_per_test < 10000:  # Less than 10 seconds
        rating = "⚠️  ACCEPTABLE"
    else:
        rating = "❌ SLOW"
    
    print(f"🏆 Performance Rating: {rating}")
    print("=" * 50)

if __name__ == "__main__":
    test_query_agent_performance() 