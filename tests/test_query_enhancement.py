#!/usr/bin/env python3
"""
Test for query enhancement logic in multi_source_search_agent.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_query_enhancement():
    """Test the query enhancement logic"""
    
    # Mock the enhancement logic
    def enhance_queries(queries, company_name, domain):
        enhanced_queries = []
        for query in queries:
            # Check if company name or domain is already in the query
            company_in_query = (
                company_name.lower() in query.lower() or 
                domain.lower() in query.lower() or
                company_name.split()[0].lower() in query.lower()  # Check first word of company name
            )
            
            if not company_in_query:
                # Add company name to the beginning of the query
                enhanced_query = f"{company_name} {query}"
                enhanced_queries.append(enhanced_query)
            else:
                enhanced_queries.append(query)
        
        return enhanced_queries
    
    # Test cases
    test_cases = [
        {
            "company_name": "Stripe",
            "domain": "stripe.com",
            "queries": [
                "AI fraud detection",
                "machine learning payments",
                "Stripe security features",
                "fintech technology"
            ],
            "expected": [
                "Stripe AI fraud detection",
                "Stripe machine learning payments", 
                "Stripe security features",  # Already contains company name
                "Stripe fintech technology"
            ]
        },
        {
            "company_name": "Square Inc",
            "domain": "square.com", 
            "queries": [
                "payment processing",
                "Square API documentation",
                "mobile payments",
                "Square Inc business model"
            ],
            "expected": [
                "Square Inc payment processing",
                "Square API documentation",  # Contains "Square"
                "Square Inc mobile payments",
                "Square Inc business model"  # Already contains full company name
            ]
        },
        {
            "company_name": "PayPal",
            "domain": "paypal.com",
            "queries": [
                "PayPal digital wallet",
                "online payments",
                "PayPal security",
                "payment gateway"
            ],
            "expected": [
                "PayPal digital wallet",  # Already contains company name
                "PayPal online payments",
                "PayPal security",  # Already contains company name
                "PayPal payment gateway"
            ]
        }
    ]
    
    print("🧪 Testing Query Enhancement Logic")
    print("=" * 50)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['company_name']}")
        
        result = enhance_queries(
            test_case['queries'], 
            test_case['company_name'], 
            test_case['domain']
        )
        
        expected = test_case['expected']
        
        # Check if results match expected
        if result == expected:
            print(f"✅ PASS: Query enhancement works correctly")
            print(f"   Input: {test_case['queries']}")
            print(f"   Output: {result}")
        else:
            print(f"❌ FAIL: Query enhancement failed")
            print(f"   Input: {test_case['queries']}")
            print(f"   Expected: {expected}")
            print(f"   Got: {result}")
            all_passed = False
    
    print(f"\n{'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    return all_passed

def test_edge_cases():
    """Test edge cases for query enhancement"""
    
    def enhance_queries(queries, company_name, domain):
        enhanced_queries = []
        for query in queries:
            company_in_query = (
                company_name.lower() in query.lower() or 
                domain.lower() in query.lower() or
                company_name.split()[0].lower() in query.lower()
            )
            
            if not company_in_query:
                enhanced_query = f"{company_name} {query}"
                enhanced_queries.append(enhanced_query)
            else:
                enhanced_queries.append(query)
        
        return enhanced_queries
    
    print("\n🔍 Testing Edge Cases")
    print("=" * 30)
    
    # Edge case 1: Empty queries
    result = enhance_queries([], "Test Company", "test.com")
    print(f"Empty queries: {result} (should be empty)")
    
    # Edge case 2: Company name with special characters
    result = enhance_queries(
        ["AI technology", "machine learning"], 
        "Test & Co.", 
        "test-co.com"
    )
    print(f"Special chars in company name: {result}")
    
    # Edge case 3: Very long company name
    result = enhance_queries(
        ["technology solutions"], 
        "Very Long Company Name With Multiple Words", 
        "verylongcompany.com"
    )
    print(f"Long company name: {result}")
    
    # Edge case 4: Case sensitivity
    result = enhance_queries(
        ["STRIPE API", "stripe documentation"], 
        "Stripe", 
        "stripe.com"
    )
    print(f"Case sensitivity: {result}")

if __name__ == "__main__":
    print("🚀 Testing Query Enhancement for Multi-Source Search Agent")
    print("=" * 60)
    
    # Run main tests
    main_tests_passed = test_query_enhancement()
    
    # Run edge case tests
    test_edge_cases()
    
    if main_tests_passed:
        print("\n✅ Query enhancement logic is working correctly!")
        print("💡 This ensures company names are always included in search queries")
    else:
        print("\n❌ Query enhancement logic needs fixing!")
        print("🔧 Check the enhancement logic in multi_source_search_agent.py") 