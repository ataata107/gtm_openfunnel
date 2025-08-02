#!/usr/bin/env python3
"""
Test script to measure the performance of multi_source_search_agent in isolation.
"""

import time
import json
import os
import sys

# Add the parent directory to the path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from graph.state import GTMState, CompanyMeta

load_dotenv()

def create_test_state():
    """Create a test state with sample extracted companies"""
    return GTMState(
        research_goal="Find fintech companies using AI for fraud detection",
        search_depth="comprehensive",
        max_parallel_searches=100,
        confidence_threshold=0.8,
        max_iterations=2,
        iteration_count=0,
        extracted_companies=[
            CompanyMeta(
                name="Stripe",
                domain="stripe.com",
                source_url="https://stripe.com/"
            ),
            CompanyMeta(
                name="Sift",
                domain="sift.com", 
                source_url="https://sift.com/"
            ),
            CompanyMeta(
                name="Hawk AI",
                domain="hawk.ai",
                source_url="https://hawk.ai/"
            ),
            CompanyMeta(
                name="Feedzai",
                domain="feedzai.com",
                source_url="https://feedzai.com/"
            ),
            CompanyMeta(
                name="Sardine",
                domain="sardine.ai",
                source_url="https://sardine.ai/"
            )
        ]
    )

def test_multi_source_search_performance():
    """Test the multi-source search agent and measure performance"""
    
    print("🧪 Testing Multi-Source Search Agent Performance")
    print("=" * 55)
    
    # Check environment
    if not os.getenv("SERPER_API_KEY"):
        print("❌ SERPER_API_KEY not found in environment variables")
        return
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        return
    
    print("✅ Environment variables found")
    
    # Create test state
    test_state = create_test_state()
    print(f"📝 Created test state with {len(test_state.extracted_companies)} companies")
    
    # Measure performance
    print("\n⏱️  Starting performance test...")
    start_time = time.time()
    
    try:
        # Import and test
        from agents.multi_source_search_agent import multi_source_search_agent
        
        # Run the agent
        result_state = multi_source_search_agent(test_state)
        
        # Calculate timing
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        duration_seconds = end_time - start_time
        
        # Get results
        search_results = result_state.search_results_serper
        total_results = sum(len(results) for results in search_results.values()) if search_results else 0
        
        print(f"\n📊 Performance Results:")
        print(f"  ⏱️  Total Time: {duration_seconds:.2f}s ({duration_ms:.2f}ms)")
        print(f"  🏢 Companies Processed: {len(test_state.extracted_companies)}")
        print(f"  📝 Search Results: {total_results}")
        print(f"  🚀 Results per Second: {total_results / duration_seconds:.2f}")
        
        # Show search results by company
        if search_results:
            print(f"\n🔍 Search Results by Company:")
            for domain, results in search_results.items():
                print(f"  {domain}: {len(results)} results")
        
        # Save results
        os.makedirs("../debug_output", exist_ok=True)
        results = {
            "test_name": "multi_source_search_performance",
            "duration_ms": duration_ms,
            "duration_seconds": duration_seconds,
            "companies_processed": len(test_state.extracted_companies),
            "total_search_results": total_results,
            "results_per_second": total_results / duration_seconds,
            "search_results_by_company": {domain: len(results) for domain, results in search_results.items()} if search_results else {}
        }
        
        output_path = "../debug_output/multi_source_search_test_results.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n📁 Saved test results to {output_path}")
        
        return results
        
    except Exception as e:
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        print(f"\n❌ Test failed after {duration_ms:.2f}ms")
        print(f"Error: {str(e)}")
        
        # Save error results
        error_results = {
            "test_name": "multi_source_search_performance",
            "status": "error",
            "duration_ms": duration_ms,
            "error": str(e)
        }
        
        os.makedirs("../debug_output", exist_ok=True)
        output_path = "../debug_output/multi_source_search_test_error.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(error_results, f, ensure_ascii=False, indent=2)
        print(f"📁 Saved error results to {output_path}")
        
        return error_results

if __name__ == "__main__":
    results = test_multi_source_search_performance()
    if results and "error" not in results:
        print(f"\n✅ Performance testing completed!")
        print(f"Performance: {results['duration_ms']:.2f}ms for {results['companies_processed']} companies")
    else:
        print(f"\n❌ Performance testing failed!") 