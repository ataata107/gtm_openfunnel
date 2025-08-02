#!/usr/bin/env python3
"""
Simple API Test

This script tests the simple synchronous API endpoint.
Located in tests/ folder for better organization.
"""

import requests
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# API base URL
BASE_URL = "http://localhost:8001"

def test_simple_research():
    """Test the simple research endpoint"""
    print("🧪 Testing Simple API")
    print("=" * 30)
    
    # Test health check
    print("1. Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()
    
    # Test research endpoint
    print("2. Testing research endpoint...")
    research_request = {
        "research_goal": "Find fintech companies using AI for fraud detection",
        "search_depth": "comprehensive",
        "max_parallel_searches": 20,
        "confidence_threshold": 0.8,
        "max_iterations": 2
    }
    
    print(f"   Request: {research_request['research_goal']}")
    print("   ⏳ Executing research (this may take a minute)...")
    
    response = requests.post(
        f"{BASE_URL}/research",
        json=research_request
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Research completed!")
        print(f"   📊 Results:")
        print(f"      - Total Companies: {result['total_companies']}")
        print(f"      - Search Strategies: {result['search_strategies_generated']}")
        print(f"      - Total Searches: {result['total_searches_executed']}")
        print(f"      - Processing Time: {result['processing_time_ms']}ms")
        print(f"      - Status: {result['status']}")
        
        if result['results']:
            print(f"   🏢 Companies Found:")
            for company_result in result['results']:
                print(f"      - {company_result['domain']}: {company_result['confidence_score']:.2f} confidence")
    else:
        print(f"   ❌ Error: {response.text}")
    
    print()

def main():
    """Main test function"""
    print("🚀 Simple GTM Intelligence API Test")
    print("=" * 50)
    
    try:
        test_simple_research()
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print("   Make sure the server is running: python simple_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 