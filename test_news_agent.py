#!/usr/bin/env python3
"""
Test script for the news agent functionality
"""

import asyncio
import os
from dotenv import load_dotenv
from agents.news_search_agent import get_news_urls_for_queries
from agents.news_extractor_agent import extract_companies_from_news_urls

load_dotenv()

async def test_news_agent():
    """Test the news agent functionality"""
    print("🧪 Testing News Agent...")
    
    # Test queries
    test_queries = [
        "fintech companies using AI for fraud detection",
        "AI startups in financial services"
    ]
    
    try:
        # Test news URL extraction
        print("📰 Testing news URL extraction...")
        news_urls = await get_news_urls_for_queries(test_queries, max_parallel=2)
        print(f"✅ Found {len(news_urls)} news URLs")
        
        if news_urls:
            # Test company extraction from news using Playwright toolkit
            print("🏢 Testing company extraction from news using Playwright toolkit...")
            companies = await extract_companies_from_news_urls(
                news_urls[:2],  # Test with first 2 URLs (Playwright is slower)
                "fintech companies using AI for fraud detection",
                max_parallel=1  # Reduce parallelism for testing
            )
            print(f"✅ Extracted {len(companies)} companies from news")
            
            for company in companies:
                print(f"  - {company.name} ({company.domain})")
        else:
            print("⚠️ No news URLs found")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_news_agent()) 