#!/usr/bin/env python3
"""
Test Client for GTM Intelligence API

This script demonstrates how to use the REST API endpoints
for research requests and responses.

Usage:
    python test_api.py
"""

import requests
import json
import time
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_start_research():
    """Test starting a new research batch"""
    print("🚀 Testing research batch start...")
    
    # Sample research request
    research_request = {
        "research_goal": "Find fintech companies using AI for fraud detection",
        "search_depth": "comprehensive",
        "max_parallel_searches": 20,
        "confidence_threshold": 0.8,
        "max_iterations": 2
    }
    
    response = requests.post(
        f"{BASE_URL}/research/batch",
        json=research_request
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Research ID: {result['research_id']}")
    print(f"Status: {result['status']}")
    print()
    
    return result['research_id']

def test_get_research_status(research_id: str):
    """Test getting research status"""
    print(f"📊 Testing research status for {research_id}...")
    
    response = requests.get(f"{BASE_URL}/research/{research_id}/status")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Research Status: {result['status']}")
    print(f"Progress: {result['progress']}%")
    print(f"Current Step: {result['current_step']}")
    print()

def test_get_research_results(research_id: str):
    """Test getting research results"""
    print(f"📋 Testing research results for {research_id}...")
    
    response = requests.get(f"{BASE_URL}/research/{research_id}")
    print(f"Status: {response.status_code}")
    result = response.json()
    
    print(f"Research Status: {result['status']}")
    print(f"Total Companies: {result['total_companies']}")
    print(f"Search Strategies: {result['search_strategies_generated']}")
    print(f"Total Searches: {result['total_searches_executed']}")
    print(f"Processing Time: {result['processing_time_ms']}ms")
    
    if result['results']:
        print("\n📊 Sample Results:")
        for i, company_result in enumerate(result['results'][:3]):  # Show first 3
            print(f"  {i+1}. {company_result['domain']}")
            print(f"     Confidence: {company_result['confidence_score']}")
            print(f"     Evidence Sources: {company_result['evidence_sources']}")
            print(f"     Signals Found: {company_result['signals_found']}")
    
    print()

def test_list_research_sessions():
    """Test listing all research sessions"""
    print("📋 Testing list research sessions...")
    
    response = requests.get(f"{BASE_URL}/research")
    print(f"Status: {response.status_code}")
    result = response.json()
    
    print(f"Total Sessions: {len(result['sessions'])}")
    for session in result['sessions']:
        print(f"  - {session['research_id'][:8]}... ({session['status']})")
    print()

def test_delete_research_session(research_id: str):
    """Test deleting a research session"""
    print(f"🗑️ Testing delete research session {research_id}...")
    
    response = requests.delete(f"{BASE_URL}/research/{research_id}")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    print()

def monitor_research_progress(research_id: str, max_wait_time: int = 300):
    """Monitor research progress until completion"""
    print(f"⏳ Monitoring research progress for {research_id}...")
    print("(This may take a few minutes)")
    
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(f"{BASE_URL}/research/{research_id}/status")
            if response.status_code == 200:
                status = response.json()
                print(f"Status: {status['status']} | Progress: {status['progress']}% | Step: {status['current_step']}")
                
                if status['status'] in ['completed', 'failed']:
                    print(f"✅ Research {status['status']}!")
                    return status['status']
            
            time.sleep(10)  # Check every 10 seconds
            
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring interrupted by user")
            break
        except Exception as e:
            print(f"⚠️ Error monitoring progress: {e}")
            time.sleep(5)
    
    print("⏰ Monitoring timeout reached")
    return "timeout"

def main():
    """Main test function"""
    print("🧪 GTM Intelligence API Test Client")
    print("=" * 50)
    
    # Test health check
    test_health_check()
    
    # Test starting research
    research_id = test_start_research()
    
    # Monitor progress
    final_status = monitor_research_progress(research_id)
    
    if final_status == "completed":
        # Test getting results
        test_get_research_results(research_id)
    
    # Test listing sessions
    test_list_research_sessions()
    
    # Test deleting session (optional)
    # test_delete_research_session(research_id)
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    main() 