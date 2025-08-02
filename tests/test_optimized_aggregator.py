#!/usr/bin/env python3
"""
Quick test to verify the optimized company aggregator.
"""

import time
import sys
import os

# Add the parent directory to the path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from graph.state import GTMState

load_dotenv()

def quick_test():
    """Quick test of the optimized agent"""
    
    print("🚀 Quick Test of Optimized Company Aggregator")
    print("=" * 50)
    
    if not os.getenv("SERPER_API_KEY") or not os.getenv("OPENAI_API_KEY"):
        print("❌ Missing API keys")
        return
    
    # Create minimal test state
    test_state = GTMState(
        research_goal="Find fintech companies using AI for fraud detection",
        search_depth="comprehensive",
        max_parallel_searches=5,  # Reduced for quick test
        confidence_threshold=0.8,
        max_iterations=2,
        search_strategies_generated=[
            "fintech companies AI fraud detection",
            "AI fraud detection fintech startups",
            "machine learning fraud detection fintech"
        ]
    )
    
    print(f"📝 Testing with {len(test_state.search_strategies_generated)} search strategies")
    
    # Import and test
    from agents.company_aggregator_agent import company_aggregator_agent
    
    start_time = time.time()
    
    try:
        result_state = company_aggregator_agent(test_state)
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        print(f"\n📊 Results:")
        print(f"  ⏱️  Time: {duration_ms:.2f}ms ({duration_ms/1000:.2f}s)")
        print(f"  🏢 Companies: {len(result_state.extracted_companies)}")
        print(f"  📝 Strategies: {len(test_state.search_strategies_generated)}")
        
        if len(result_state.extracted_companies) > 0:
            print(f"\n🏢 Sample companies:")
            for i, company in enumerate(result_state.extracted_companies[:5], 1):
                print(f"  {i}. {company.name} ({company.domain})")
        
        return {
            "duration_ms": duration_ms,
            "companies": len(result_state.extracted_companies),
            "strategies": len(test_state.search_strategies_generated)
        }
        
    except Exception as e:
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        print(f"❌ Test failed after {duration_ms:.2f}ms: {e}")
        return None

if __name__ == "__main__":
    results = quick_test()
    if results:
        print(f"\n✅ Test completed successfully!")
        print(f"Performance: {results['duration_ms']:.2f}ms for {results['companies']} companies") 