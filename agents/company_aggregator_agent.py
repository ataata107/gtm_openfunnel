from graph.state import GTMState, CompanyMeta
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List
import asyncio
from dotenv import load_dotenv
import os
import json

from utils.cache import cache
from agents.news_extractor_agent import extract_companies_from_news_queries
from graph.state import ExtractedCompany
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.tools import Tool

load_dotenv()



SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Global search depth configuration
# Companies per query calculated based on target totals:
# Quick: 5 queries × 10 companies/query = 50 total companies
# Standard: 10 queries × 10 companies/query = 100 total companies  
# Comprehensive: 15 queries × 13-14 companies/query = 200 total companies
SEARCH_DEPTH_CONFIGS = {
    "quick": {"num_results": 10, "companies_per_query": 20, "max_companies": 50, "description": "10 results per search, 10 companies per query, 50 companies max"},
    "standard": {"num_results": 20, "companies_per_query": 20, "max_companies": 100, "description": "20 results per search, 10 companies per query, 100 companies max"},
    "comprehensive": {"num_results": 30, "companies_per_query": 28, "max_companies": 200, "description": "30 results per search, 14 companies per query, 200 companies max"}
}

class CompanyExtractionOutput(BaseModel):
    companies: List[ExtractedCompany]

# Global LLM with Serper tools
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Create Serper search wrapper and tool
search = GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY)
serper_tool = Tool(
    name="search",
    func=search.run,
    description="Search the web using Serper to find information about companies relevant to the research goal."
)


llm_with_tools = llm.bind_tools([serper_tool])
llm_with_output = llm.with_structured_output(CompanyExtractionOutput)

async def extract_companies_with_serper_tool(query: str, research_goal: str, search_depth: str = "standard") -> List[ExtractedCompany]:
    """Extract companies directly using LLM with Serper tools"""
    try:
        # Check cache first
        cache_key = f"companies:{query}:{search_depth}"
        cached_results = await cache.get(cache_key)
        if cached_results:
            print(f"✅ Cache hit for companies from query: {query}")
            return cached_results
        
        # Configure search depth
        config = SEARCH_DEPTH_CONFIGS.get(search_depth, SEARCH_DEPTH_CONFIGS["standard"])
        num_results = config["num_results"]
        companies_per_query = config["companies_per_query"]
        
        # Update search wrapper with correct number of results
        search.k = num_results
        
        # Direct message to LLM with tools
        message = f"""
        Please search for companies relevant to this research goal: {research_goal}
        
        Use the search tool to find information about companies that match this research objective.
        Search for terms like "{query}" and related keywords to find relevant companies.
        
        IMPORTANT: Extract atmost {companies_per_query} companies. 
        Include companies that are:
        - Directly relevant to the research goal
        - Related to the industry or technology mentioned
        - Competitors or similar companies
        - Companies mentioned in articles, lists, or comparisons
        
        Return atmost {companies_per_query} companies with their names and domains.
        Focus on quality and relevance over quantity.
        """
        
        # Let the LLM use the search tool directly
        response = await llm_with_output.ainvoke(message)
        companies = response.companies
        
        # Cache the results
        await cache.set(cache_key, companies, ttl=7200)
        
        # print(f"🔍 Extracted {len(companies)} companies from query: {query}")
        return companies
        
    except Exception as e:
        print(f"❌ Failed to extract companies from {query}: {e}")
        return []

def company_aggregator_agent(state: GTMState) -> GTMState:
    print("🏢 COMPANY AGGREGATOR: Starting company extraction...")
    print(f"📋 Research Goal: {state.research_goal}")
    print(f"🔍 Search Strategies: {len(state.search_strategies_generated)}")
    print(f"🎯 Search Depth: {state.search_depth}")
    
    if not state.search_strategies_generated:
        raise ValueError("Missing search strategies")

    if not SERPER_API_KEY:
        raise ValueError("SERPER_API_KEY not found in environment variables")

    # Configure company limits based on search depth
    config = SEARCH_DEPTH_CONFIGS.get(state.search_depth, SEARCH_DEPTH_CONFIGS["standard"])
    max_companies = config["max_companies"]
    companies_per_query = config["companies_per_query"]
    num_queries = len(state.search_strategies_generated)
    expected_total = num_queries * companies_per_query
    
    print(f"🎯 COMPANY AGGREGATOR: Targeting {config['description']}")
    print(f"📊 Expected: {num_queries} queries × {companies_per_query} companies/query = {expected_total} total companies")
    print(f"🎯 Max companies limit: {max_companies}")
    
    extracted_companies = []
    seen_domains = set()

    print("🔍 Running Serper with LLM tools to extract companies...")
    
    # TIME SERPER + LLM EXTRACTION
    import time
    extraction_start = time.time()
    
    async def extract_all_companies():
        sem = asyncio.Semaphore(state.max_parallel_searches)
        
        async def extract_single_query(query):
            async with sem:
                try:
                    companies = await extract_companies_with_serper_tool(
                        query, 
                        state.research_goal, 
                        state.search_depth
                    )
                    
                    # Filter out duplicates
                    unique_companies = []
                    for company in companies:
                        if company.domain not in seen_domains:
                            unique_companies.append(company)
                            seen_domains.add(company.domain)
                    
                    # print(f"🔍 Extracted {len(unique_companies)} unique companies from query: {query}")
                    return unique_companies
                    
                except Exception as e:
                    print(f"❌ Failed to extract companies from {query}: {e}")
                    return []

        # Run all extractions in parallel
        tasks = [extract_single_query(query) for query in state.search_strategies_generated]
        all_results = await asyncio.gather(*tasks)
        
        # Combine all results
        for companies in all_results:
            for company in companies:
                extracted_companies.append(CompanyMeta(**company.dict()))
                
                # Stop if we've reached the company limit
                if len(extracted_companies) >= max_companies:
                    print(f"🎯 COMPANY AGGREGATOR: Reached company limit ({max_companies})")
                    break
            # Stop if we've reached the company limit
            if len(extracted_companies) >= max_companies:
                break

    # Run the async extraction
    asyncio.run(extract_all_companies())
    
    extraction_end = time.time()
    extraction_duration = (extraction_end - extraction_start) * 1000
    print(f"⏱️  Serper + LLM extraction took: {extraction_duration:.2f}ms ({extraction_duration/1000:.2f}s)")
    print(f"🔍 Serper extracted {len(extracted_companies)} companies")
    
    # NEW: NEWS-BASED EXTRACTION
    print("📰 Starting news-based company extraction...")
    news_start = time.time()
    
    async def extract_news_companies():
        try:
            # Extract companies from news using unified LLM approach
            news_companies = await extract_companies_from_news_queries(
                state.search_strategies_generated, 
                state.research_goal,
                search_depth=state.search_depth,  # Pass search depth for consistent limits
                max_parallel=state.max_parallel_searches  # Limit parallel processing
            )
            
            # Add news companies to existing list (avoiding duplicates)
            for company in news_companies:
                if company.domain not in seen_domains:
                    seen_domains.add(company.domain)
                    extracted_companies.append(CompanyMeta(**company.dict()))
                    
                    # # Stop if we've reached the company limit
                    # if len(extracted_companies) >= max_companies:
                    #     print(f"🎯 COMPANY AGGREGATOR: Reached company limit ({max_companies})")
                    #     break
            
            print(f"📰 Added {len(news_companies)} companies from news articles")
                
        except Exception as e:
            print(f"❌ News extraction failed: {e}")
    
    # Run the async news extraction
    asyncio.run(extract_news_companies())
    
    news_end = time.time()
    news_duration = (news_end - news_start) * 1000
    print(f"⏱️  News extraction took: {news_duration:.2f}ms ({news_duration/1000:.2f}s)")
    
    total_duration = (news_end - extraction_start) * 1000
    print(f"⏱️  Total time: {total_duration:.2f}ms ({total_duration/1000:.2f}s)")

    # ✅ Save to disk for debugging
    os.makedirs("debug_output", exist_ok=True)
    output_path = os.path.join("debug_output", "extracted_companies.json")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([c.dict() for c in extracted_companies], f, ensure_ascii=False, indent=2)
        print(f"📁 Saved {len(extracted_companies)} companies to {output_path}")
    except Exception as e:
        print(f"⚠️ Failed to write extracted companies: {e}")

    return state.model_copy(update={"extracted_companies": extracted_companies})
