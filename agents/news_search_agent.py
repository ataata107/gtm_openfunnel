# agents/news_search_agent.py

import asyncio
import os
import json
import requests
from typing import List
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

async def run_serper_news(query: str, sem: asyncio.Semaphore, num_results: int = 10):
    """Get news URLs from Serper news API"""
    async with sem:
        try:
            # Check cache first
            from utils.cache import cache
            cached_results = await cache.get_search_results(query, "serper_news")
            if cached_results:
                print(f"✅ Cache hit for news query: {query}")
                return cached_results
            
            url = "https://google.serper.dev/news"
            payload = {"q": query, "num": num_results}
            headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
            
            # Make the API call
            response = await asyncio.to_thread(
                requests.post, url, headers=headers, json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                news_links = [item["link"] for item in data.get("news", [])]
                print(f"📰 Found {len(news_links)} news articles for query: {query}")
                
                # Cache the results
                await cache.set_search_results(query, "serper_news", news_links, ttl=7200)
                return news_links
            else:
                print(f"❌ Serper news API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Serper news search failed for '{query}': {e}")
            return []

async def get_news_urls_for_queries(queries: List[str], max_parallel: int = 5) -> List[str]:
    """Get news URLs for multiple queries"""
    sem = asyncio.Semaphore(max_parallel)
    tasks = [run_serper_news(query, sem) for query in queries]
    results = await asyncio.gather(*tasks)
    
    # Flatten and deduplicate URLs
    all_urls = []
    seen_urls = set()
    
    for urls in results:
        for url in urls:
            if url not in seen_urls:
                all_urls.append(url)
                seen_urls.add(url)
    
    print(f"📰 Total unique news URLs found: {len(all_urls)}")
    return all_urls 