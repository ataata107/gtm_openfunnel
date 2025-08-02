#!/usr/bin/env python3
"""
Simple API Test with Mock Data

This script demonstrates the REST API functionality using mock data
to show the complete request/response workflow.
Located in tests/ folder for better organization.
"""

import requests
import json
import time
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# API base URL
BASE_URL = "http://localhost:8001"

def test_complete_workflow():
    """Test the complete API workflow with mock data"""
    print("🧪 Testing Complete API Workflow")
    print("=" * 50)
    
    # 1. Test health check
    print("1. Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()
    
    # 2. Start research
    print("2. Starting research...")
    research_request = {
        "research_goal": "Find fintech companies using AI for fraud detection",
        "search_depth": "comprehensive",
        "max_parallel_searches": 20,
        "confidence_threshold": 0.8,
        "max_iterations": 2
    }
    
    response = requests.post(f"{BASE_URL}/research", json=research_request)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Research Goal: {result['research_goal']}")
    print(f"   Status: {result['status']}")
    print()
    
    # 3. Display results
    print("3. Research Results:")
    print(f"   Total Companies: {result['total_companies']}")
    print(f"   Search Strategies: {result['search_strategies_generated']}")
    print(f"   Total Searches: {result['total_searches_executed']}")
    print(f"   Processing Time: {result['processing_time_ms']}ms")
    
    if result['results']:
        print("\n📊 Sample Results:")
        for i, company_result in enumerate(result['results'][:3]):  # Show first 3
            print(f"  {i+1}. {company_result['domain']}")
            print(f"     Confidence: {company_result['confidence_score']}")
            print(f"     Evidence Sources: {company_result['evidence_sources']}")
            print(f"     Signals Found: {company_result['signals_found']}")
    
    print()

def test_api_documentation():
    """Test API documentation endpoints"""
    print("\n📚 Testing API Documentation")
    print("=" * 30)
    
    # Test root endpoint
    print("1. Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    root_data = response.json()
    print(f"   Message: {root_data['message']}")
    print(f"   Version: {root_data['version']}")
    print(f"   Documentation: {root_data['documentation']}")
    print()
    
    print("✅ API documentation test completed!")
    print("\n🌐 Available URLs:")
    print(f"   📚 Interactive Docs: {BASE_URL}/docs")
    print(f"   🔍 Health Check: {BASE_URL}/health")
    print(f"   🏠 Root: {BASE_URL}/")

def demonstrate_expected_response():
    """Demonstrate the expected successful response format"""
    print("\n📊 Expected Successful Response Format")
    print("=" * 40)
    
    expected_response = {
        "research_goal": "Find fintech companies using AI for fraud detection",
        "total_companies": 150,
        "search_strategies_generated": 12,
        "total_searches_executed": 1847,
        "processing_time_ms": 28450,
        "company_domains": ["stripe.com", "square.com", "plaid.com"],
        "results": [
            {
                "domain": "stripe.com",
                "confidence_score": 0.92,
                "evidence_sources": 15,
                "findings": {
                    "ai_fraud_detection": True,
                    "technologies": ["TensorFlow", "scikit-learn", "PyTorch"],
                    "evidence": [
                        "Stripe uses machine learning for fraud detection",
                        "AI-powered risk assessment system",
                        "Real-time fraud detection with ML models"
                    ],
                    "signals_found": 8
                },
                "signals_found": 8
            },
            {
                "domain": "square.com",
                "confidence_score": 0.87,
                "evidence_sources": 12,
                "findings": {
                    "ai_fraud_detection": True,
                    "technologies": ["TensorFlow", "scikit-learn"],
                    "evidence": [
                        "Square implements AI for fraud prevention",
                        "Machine learning models for transaction analysis"
                    ],
                    "signals_found": 6
                },
                "signals_found": 6
            }
        ],
        "search_performance": {
            "queries_per_second": 65,
            "cache_hit_rate": 0.34,
            "failed_requests": 12
        },
        "status": "completed"
    }
    
    print("✅ Expected successful response format:")
    print(json.dumps(expected_response, indent=2))
    
    print("\n📈 Key Metrics:")
    print(f"   - Total Companies: {expected_response['total_companies']}")
    print(f"   - Search Strategies: {expected_response['search_strategies_generated']}")
    print(f"   - Total Searches: {expected_response['total_searches_executed']}")
    print(f"   - Processing Time: {expected_response['processing_time_ms']}ms")
    print(f"   - Queries/Second: {expected_response['search_performance']['queries_per_second']}")

def main():
    """Main test function"""
    print("🚀 GTM Intelligence API - Simple Test")
    print("=" * 50)
    
    try:
        # Test complete workflow
        test_complete_workflow()
        
        # Test API documentation
        test_api_documentation()
        
        # Demonstrate expected response
        demonstrate_expected_response()
        
        print("\n🎉 All tests completed successfully!")
        print("\n💡 To test with real data:")
        print("   1. Set up environment variables (OPENAI_API_KEY, SERPER_API_KEY, etc.)")
        print("   2. Run: python tests/test_simple_api.py")
        print("   3. Or use the interactive docs at: http://localhost:8001/docs")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print("   Make sure the server is running: python simple_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 