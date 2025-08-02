#!/usr/bin/env python3
"""
Test script for the async extract agent
"""

import os
import sys
from graph.state import GTMState, CompanyMeta
from agents.async_extract_agent import async_extract_agent

def test_async_extract_agent():
    """Test the async extract agent with sample companies"""
    
    # Create sample state with companies
    sample_companies = [
        CompanyMeta(domain="stripe.com", name="Stripe", industry="Fintech"),
        CompanyMeta(domain="square.com", name="Square", industry="Fintech"),
    ]
    
    state = GTMState(
        research_goal="Find fintech companies using AI for fraud detection",
        extracted_companies=sample_companies,
        max_parallel_searches=5,
        confidence_threshold=0.8
    )
    
    print("🧪 Testing Async Extract Agent...")
    print(f"📋 Companies to process: {[c.domain for c in sample_companies]}")
    
    try:
        # Run the async extract agent
        result_state = async_extract_agent(state)
        
        print("\n✅ Async Extract Agent completed!")
        print(f"📊 Results: {result_state.search_results_website}")
        
        if result_state.search_results_website:
            print("\n🎯 Extracted Data:")
            for domain, data in result_state.search_results_website.items():
                print(f"\n📌 {domain}:")
                print(f"  Uses AI: {data.get('uses_ai', 'N/A')}")
                print(f"  Evidence: {data.get('ai_evidence', 'N/A')}")
                print(f"  Technologies: {data.get('ai_technologies', [])}")
                print(f"  Confidence: {data.get('confidence_score', 'N/A')}")
        else:
            print("❌ No results extracted")
            
    except Exception as e:
        print(f"❌ Error testing async extract agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_async_extract_agent() 