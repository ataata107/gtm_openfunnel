# agents/news_extractor_agent.py

import asyncio
import os
import json
from typing import List
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from graph.state import ExtractedCompany
from dotenv import load_dotenv

import nest_asyncio
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.tools import Tool

load_dotenv()
nest_asyncio.apply()



SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Global search depth configuration - same as company_aggregator_agent
SEARCH_DEPTH_CONFIGS = {
    "quick": {"num_results": 40, "companies_per_query": 20, "max_companies": 50, "description": "10 results per search, 10 companies per query, 50 companies max"},
    "standard": {"num_results": 40, "companies_per_query": 20, "max_companies": 100, "description": "20 results per search, 10 companies per query, 100 companies max"},
    "comprehensive": {"num_results": 40, "companies_per_query": 28, "max_companies": 200, "description": "30 results per search, 14 companies per query, 200 companies max"}
}

class CompanyExtractionOutput(BaseModel):
    companies: List[ExtractedCompany]

# Global LLM setup with both Serper news and Playwright tools
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Create Serper news search wrapper and tool
news_search = GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY, type="news", k=40)
news_search_tool = Tool(
    name="news_search",
    func=news_search.run,
    description="Search for recent news articles using Serper news API. Use this to find news articles about companies relevant to the research goal."
)

llm_with_output = llm.with_structured_output(CompanyExtractionOutput)

async def extract_companies_from_news_queries(queries: List[str], research_goal: str, search_depth: str = "standard", max_parallel: int = 3) -> List[ExtractedCompany]:
    """Extract companies from news using LLM with Serper news search and Playwright tools"""
    all_companies = []
    seen_domains = set()
    
    # Configure search depth
    config = SEARCH_DEPTH_CONFIGS.get(search_depth, SEARCH_DEPTH_CONFIGS["standard"])
    companies_per_query = config["companies_per_query"]
    max_companies = config["max_companies"]
    num_results = config["num_results"]
    
    # Configure news search results based on search depth
    # news_search.k = num_results
    
    print(f"📰 NEWS EXTRACTOR: Using {search_depth} search depth")
    print(f"📊 Target: {companies_per_query} companies per query, {max_companies} max total")
    print(f"🔍 News search results: {num_results} per query")
    
    # Create browser and tools within the function scope
    async_browser = create_async_playwright_browser(headless=True)
    toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
    browser_tools = toolkit.get_tools()
    
    # Combine Serper news tool with browser tools
    all_tools = [news_search_tool] + browser_tools
    llm_with_tools = llm.bind_tools(all_tools)
    
    try:
        # Process queries in batches
        sem = asyncio.Semaphore(max_parallel)
        
        async def process_single_query(query: str):
            async with sem:
                try:
                    # Message to LLM with both news search and browser tools
                    message = f"""
                    Please search for news articles about companies relevant to this goal: {research_goal}
                    
                    Use the news_search tool to find recent news article links about companies satisfying the goal.
                    Then use the browser tools to visit all the links you get from news search and extract companies.
                    
                    IMPORTANT: Extract AT LEAST 15-20 companies from the news article links. Be extremely thorough and comprehensive.
                    Include companies that are:
                    - Directly relevant to the goal
                    - Competitors or similar companies mentioned in articles
                    - Companies featured in news, lists, or comparisons
                    - Companies mentioned in quotes, interviews, or case studies
                    - Companies from different market segments
                    - Both established and emerging companies
                    - Companies mentioned in case studies, reports, or reviews
                    - Companies from different geographical regions
                    
                    Search multiple news sources and visit multiple articles to find more companies.
                    Return AT LEAST 15-20 companies with their names and domains.
                    Focus on comprehensive coverage over perfect relevance.
                    """
                    
                    # Let the LLM use both tools directly
                    response = await llm_with_output.ainvoke(message)
                    companies = response.companies
                    
                    # Filter out duplicates
                    unique_companies = []
                    for company in companies:
                        if company.domain not in seen_domains:
                            unique_companies.append(company)
                            seen_domains.add(company.domain)
                    
                    # print(f"📰 Extracted {len(unique_companies)} companies from query: {query}")
                    return unique_companies
                    
                except Exception as e:
                    print(f"❌ Failed to process query {query}: {e}")
                    return []
        
        # Process all queries
        tasks = [process_single_query(query) for query in queries]
        results = await asyncio.gather(*tasks)
        
        # Combine all results with limit check
        for companies in results:
            for company in companies:
                
                all_companies.append(company)
                
                
                # Stop if we've reached the company limit
                if len(all_companies) >= max_companies:
                    print(f"🎯 NEWS EXTRACTOR: Reached company limit ({max_companies})")
                    break
            # Stop if we've reached the company limit
            if len(all_companies) >= max_companies:
                break
        
        print(f"📰 Total companies extracted from news: {len(all_companies)}")
        
        # Save extracted companies to debug file
        try:
            os.makedirs("debug_output", exist_ok=True)
            output_path = os.path.join("debug_output", "news_extracted_companies.json")
            
            # Convert to serializable format
            companies_data = []
            for company in all_companies:
                companies_data.append({
                    "name": company.name,
                    "domain": company.domain,
                    "source": "news_agent"
                })
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(companies_data, f, ensure_ascii=False, indent=2)
            print(f"📁 Saved news extracted companies to {output_path}")
            
        except Exception as e:
            print(f"⚠️ Failed to write news extracted companies: {e}")
        
    finally:
        # Always close the browser
        await async_browser.close()
    
    return all_companies 