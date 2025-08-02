#!/usr/bin/env python3
"""
Test script to measure the performance of company_aggregator_agent in isolation.
"""

import time
import json
import os
import sys

# Add the parent directory to the path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from graph.state import GTMState
from agents.company_aggregator_agent import company_aggregator_agent

load_dotenv()

def create_test_state():
    """Create a test state with sample search strategies"""
    return GTMState(
        research_goal="Find fintech companies using AI for fraud detection",
        search_depth="comprehensive",
        max_parallel_searches=10,  # Reduced for testing
        confidence_threshold=0.8,
        max_iterations=2,
        search_strategies_generated=[
            "fintech companies AI fraud detection",
            "AI fraud detection fintech startups",
            "machine learning fraud detection fintech",
            "fraud detection software fintech companies",
            "AI fraud prevention fintech",
            "fraud detection algorithms fintech",
            "fintech fraud detection case studies",
            "AI fraud detection implementation fintech",
            "fraud detection API fintech",
            "fintech companies using AI for fraud"
        ]
    )

def test_company_aggregator_performance():
    """Test the company aggregator agent and measure performance"""
    
    print("🧪 Testing Company Aggregator Agent Performance")
    print("=" * 50)
    
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
    print(f"📝 Created test state with {len(test_state.search_strategies_generated)} search strategies")
    
    # Measure performance
    print("\n⏱️  Starting performance test...")
    start_time = time.time()
    
    try:
        # Run the agent
        result_state = company_aggregator_agent(test_state)
        
        # Calculate timing
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        duration_seconds = end_time - start_time
        
        # Get results
        companies_extracted = len(result_state.extracted_companies)
        
        print(f"\n📊 Performance Results:")
        print(f"  ⏱️  Total Time: {duration_seconds:.2f}s ({duration_ms:.2f}ms)")
        print(f"  🏢 Companies Extracted: {companies_extracted}")
        print(f"  📝 Search Strategies: {len(test_state.search_strategies_generated)}")
        print(f"  🚀 Queries per Second: {len(test_state.search_strategies_generated) / duration_seconds:.2f}")
        
        # Show extracted companies
        if companies_extracted > 0:
            print(f"\n🏢 Extracted Companies:")
            for i, company in enumerate(result_state.extracted_companies, 1):
                print(f"  {i}. {company.name} ({company.domain})")
                print(f"     Source: {company.source_url}")
        
        # Check for errors
        error_count = 0
        for company in result_state.extracted_companies:
            if not company.name or not company.domain:
                error_count += 1
        
        if error_count > 0:
            print(f"\n⚠️  Found {error_count} companies with missing data")
        
        # Save results
        os.makedirs("../debug_output", exist_ok=True)
        results = {
            "test_name": "company_aggregator_performance",
            "duration_ms": duration_ms,
            "duration_seconds": duration_seconds,
            "companies_extracted": companies_extracted,
            "search_strategies": len(test_state.search_strategies_generated),
            "queries_per_second": len(test_state.search_strategies_generated) / duration_seconds,
            "extracted_companies": [c.dict() for c in result_state.extracted_companies]
        }
        
        output_path = "../debug_output/company_aggregator_test_results.json"
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
            "test_name": "company_aggregator_performance",
            "status": "error",
            "duration_ms": duration_ms,
            "error": str(e)
        }
        
        os.makedirs("../debug_output", exist_ok=True)
        output_path = "../debug_output/company_aggregator_test_error.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(error_results, f, ensure_ascii=False, indent=2)
        print(f"📁 Saved error results to {output_path}")
        
        return error_results

def test_with_different_parallel_settings():
    """Test with different parallel search settings"""
    
    print("\n🧪 Testing Different Parallel Settings")
    print("=" * 50)
    
    settings = [1, 5, 10, 20]
    results = {}
    
    for max_parallel in settings:
        print(f"\n🔧 Testing with max_parallel_searches = {max_parallel}")
        
        test_state = create_test_state()
        test_state.max_parallel_searches = max_parallel
        
        start_time = time.time()
        
        try:
            result_state = company_aggregator_agent(test_state)
            
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            results[max_parallel] = {
                "duration_ms": duration_ms,
                "companies_extracted": len(result_state.extracted_companies),
                "status": "success"
            }
            
            print(f"  ✅ Success: {duration_ms:.2f}ms, {len(result_state.extracted_companies)} companies")
            
        except Exception as e:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            results[max_parallel] = {
                "duration_ms": duration_ms,
                "error": str(e),
                "status": "error"
            }
            
            print(f"  ❌ Error: {duration_ms:.2f}ms - {str(e)}")
    
    # Save comparison results
    os.makedirs("../debug_output", exist_ok=True)
    output_path = "../debug_output/parallel_settings_comparison.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n📁 Saved parallel settings comparison to {output_path}")
    
    # Show summary
    print(f"\n📊 Parallel Settings Summary:")
    for setting, result in results.items():
        if result["status"] == "success":
            print(f"  {setting} parallel: {result['duration_ms']:.2f}ms, {result['companies_extracted']} companies")
        else:
            print(f"  {setting} parallel: {result['duration_ms']:.2f}ms, ERROR")
    
    return results

if __name__ == "__main__":
    print("🚀 Company Aggregator Agent Performance Test")
    print("=" * 60)
    
    # Run basic test
    basic_results = test_company_aggregator_performance()
    
    # Run parallel settings test
    # parallel_results = test_with_different_parallel_settings()
    
    print("\n✅ Performance testing completed!")
    print("Check debug_output/ for detailed results.") 