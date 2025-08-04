#!/usr/bin/env python3
"""
Detailed performance analysis for query agent
"""

import time
import statistics
from agents.query_agent import query_agent
from graph.state import GTMState

def detailed_performance_analysis():
    """Run detailed performance analysis with multiple iterations"""
    
    test_cases = [
        {
            "name": "Quick Search",
            "research_goal": "Find fintech companies using AI for fraud detection",
            "search_depth": "quick",
            "iterations": 3
        },
        {
            "name": "Standard Search",
            "research_goal": "Find B2B SaaS companies with 50-200 employees raising Series A in 2024", 
            "search_depth": "standard",
            "iterations": 3
        },
        {
            "name": "Comprehensive Search",
            "research_goal": "Find companies using Kubernetes in production with recent security incidents",
            "search_depth": "comprehensive",
            "iterations": 3
        }
    ]
    
    print("🔬 DETAILED QUERY AGENT PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    results = {}
    
    for test_case in test_cases:
        print(f"\n📋 Analyzing: {test_case['name']}")
        print(f"🎯 Research Goal: {test_case['research_goal']}")
        print(f"🔍 Search Depth: {test_case['search_depth']}")
        print(f"🔄 Iterations: {test_case['iterations']}")
        
        times = []
        strategy_counts = []
        
        for i in range(test_case['iterations']):
            print(f"  🔄 Iteration {i+1}/{test_case['iterations']}...")
            
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
            
            times.append(execution_time)
            strategy_counts.append(strategies_generated)
            
            print(f"    ⏱️  Time: {execution_time:.2f}ms")
            print(f"    📊 Strategies: {strategies_generated}")
        
        # Calculate statistics
        avg_time = statistics.mean(times)
        std_time = statistics.stdev(times) if len(times) > 1 else 0
        min_time = min(times)
        max_time = max(times)
        
        avg_strategies = statistics.mean(strategy_counts)
        
        print(f"\n📊 {test_case['name']} Results:")
        print(f"  ⏱️  Average Time: {avg_time:.2f}ms ± {std_time:.2f}ms")
        print(f"  ⏱️  Min Time: {min_time:.2f}ms")
        print(f"  ⏱️  Max Time: {max_time:.2f}ms")
        print(f"  📊 Average Strategies: {avg_strategies:.1f}")
        print(f"  📈 Time per Strategy: {avg_time/avg_strategies:.2f}ms")
        
        results[test_case['name']] = {
            'avg_time': avg_time,
            'std_time': std_time,
            'min_time': min_time,
            'max_time': max_time,
            'avg_strategies': avg_strategies,
            'time_per_strategy': avg_time/avg_strategies
        }
    
    # Overall analysis
    print("\n" + "=" * 60)
    print("📊 OVERALL PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    all_times = [result['avg_time'] for result in results.values()]
    all_strategies = [result['avg_strategies'] for result in results.values()]
    
    print(f"⏱️  Average Time Across All Tests: {statistics.mean(all_times):.2f}ms")
    print(f"📊 Average Strategies Generated: {statistics.mean(all_strategies):.1f}")
    print(f"📈 Average Time per Strategy: {statistics.mean(all_times)/statistics.mean(all_strategies):.2f}ms")
    
    # Performance comparison
    print(f"\n🏆 Performance Comparison:")
    for name, result in results.items():
        efficiency = result['avg_strategies'] / (result['avg_time'] / 1000)  # strategies per second
        print(f"  {name}: {efficiency:.1f} strategies/second")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"  🚀 Quick searches are fastest: {results['Quick Search']['avg_time']:.0f}ms")
    print(f"  📊 Standard searches are balanced: {results['Standard Search']['avg_time']:.0f}ms")
    print(f"  🔍 Comprehensive searches are thorough: {results['Comprehensive Search']['avg_time']:.0f}ms")
    
    # Performance rating
    avg_time_across_tests = statistics.mean(all_times)
    if avg_time_across_tests < 3000:
        rating = "🚀 EXCELLENT"
        recommendation = "Ready for production use"
    elif avg_time_across_tests < 6000:
        rating = "✅ GOOD"
        recommendation = "Suitable for most use cases"
    elif avg_time_across_tests < 10000:
        rating = "⚠️  ACCEPTABLE"
        recommendation = "Consider optimization for high-volume usage"
    else:
        rating = "❌ SLOW"
        recommendation = "Needs optimization before production"
    
    print(f"\n🏆 Overall Performance Rating: {rating}")
    print(f"💡 Recommendation: {recommendation}")
    print("=" * 60)

if __name__ == "__main__":
    detailed_performance_analysis() 