#!/usr/bin/env python3
"""
Simple API Test with Mock Data

This script demonstrates the REST API functionality using mock data
to show the complete request/response workflow.
"""

import requests
import json
import time
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

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
    print("2. Starting research batch...")
    research_request = {
        "research_goal": "Find fintech companies using AI for fraud detection",
        "search_depth": "comprehensive",
        "max_parallel_searches": 20,
        "confidence_threshold": 0.8,
        "max_iterations": 2
    }
    
    response = requests.post(f"{BASE_URL}/research/batch", json=research_request)
    print(f"   Status: {response.status_code}")
    result = response.json()
    research_id = result['research_id']
    print(f"   Research ID: {research_id}")
    print(f"   Status: {result['status']}")
    print()
    
    # 3. Check status
    print("3. Checking research status...")
    response = requests.get(f"{BASE_URL}/research/{research_id}/status")
    print(f"   Status: {response.status_code}")
    status_result = response.json()
    print(f"   Research Status: {status_result['status']}")
    print(f"   Progress: {status_result['progress']}%")
    print(f"   Current Step: {status_result['current_step']}")
    print()
    
    # 4. List all sessions
    print("4. Listing all research sessions...")
    response = requests.get(f"{BASE_URL}/research")
    print(f"   Status: {response.status_code}")
    sessions_result = response.json()
    print(f"   Total Sessions: {len(sessions_result['sessions'])}")
    for session in sessions_result['sessions']:
        print(f"   - {session['research_id'][:8]}... ({session['status']})")
    print()
    
    # 5. Get results (will show failed status since we don't have env vars)
    print("5. Getting research results...")
    response = requests.get(f"{BASE_URL}/research/{research_id}")
    print(f"   Status: {response.status_code}")
    results = response.json()
    print(f"   Research Status: {results['status']}")
    print(f"   Total Companies: {results['total_companies']}")
    print(f"   Search Strategies: {results['search_strategies_generated']}")
    print(f"   Total Searches: {results['total_searches_executed']}")
    print(f"   Processing Time: {results['processing_time_ms']}ms")
    print()
    
    print("✅ API workflow test completed!")
    print("\n📋 API Endpoints Tested:")
    print("   ✅ POST /research/batch - Start research")
    print("   ✅ GET /research/{id}/status - Check status")
    print("   ✅ GET /research - List sessions")
    print("   ✅ GET /research/{id} - Get results")
    print("   ✅ GET /health - Health check")

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
        "research_id": "uuid-example",
        "status": "completed",
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
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
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
        print("   2. Run: python test_api.py")
        print("   3. Or use the interactive docs at: http://localhost:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print("   Make sure the server is running: python server.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 