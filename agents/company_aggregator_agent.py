from graph.state import GTMState, CompanyMeta
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List
import asyncio
from dotenv import load_dotenv
import os
import json
import requests
import logging
from utils.cache import cache
from agents.news_search_agent import get_news_urls_for_queries
from agents.news_extractor_agent import extract_companies_from_news_urls
from graph.state import ExtractedCompany

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Global search depth configuration
SEARCH_DEPTH_CONFIGS = {
    "quick": {"num_results": 10, "max_companies": 50, "description": "15 results per search, 50 companies max"},
    "standard": {"num_results": 20, "max_companies": 100, "description": "20 results per search, 100 companies max"},
    "comprehensive": {"num_results": 30, "max_companies": 200, "description": "30 results per search, 200 companies max"}
}


    #source_url: str = Field(..., description="The URL where the company was found")

class CompanyExtractionOutput(BaseModel):
    companies: List[ExtractedCompany]

class LLMCompanyExtractor:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.structured_llm = self.llm.with_structured_output(CompanyExtractionOutput)

        self.prompt = PromptTemplate.from_template(
            """You are an expert at parsing company intelligence from web search results.

Your goal: Extract distinct companies relevant to the following research objective:

Research Goal: {research_goal}

Given the following raw text from a search engine result, extract all **unique companies** that match the research goal.Try to extract as many companies as possible.

Consider the research goal holistically - it could be about:
- Technology adoption (e.g., AI, blockchain, cloud computing)
- Business practices (e.g., remote work, sustainability, diversity)
- Market positioning (e.g., B2B, enterprise, startup)
- Industry focus (e.g., fintech, healthcare, education)
- Company characteristics (e.g., size, funding, growth stage)
- Product capabilities (e.g., features, integrations, APIs)
- Operational aspects (e.g., security, compliance, scalability)

Extraction guidelines:
1. Look for company names mentioned in titles, snippets, or URLs
2. Extract both well-known and emerging companies
3. Focus on companies that align with the research goal
4. Include companies mentioned in case studies, partnerships, or comparisons
5. Consider industry-specific terminology and context
6. Look for companies in different stages (startups, scale-ups, enterprises)

Return a list of companies with:
- Company name (use the most common/recent name)
- Domain (e.g., stripe.com, company.com)

Only return a list of Pydantic models with the fields: name, domain.

Raw search result:
{search_result}
"""
        )

    def extract(self, search_result: str, research_goal: str) -> List[ExtractedCompany]:
        input_text = self.prompt.format(
            search_result=search_result,
            research_goal=research_goal
        )
        return self.structured_llm.invoke(input_text).companies

async def run_serper(query: str, sem: asyncio.Semaphore, search_depth: str = "standard"):
    async with sem:
        try:
            # Check cache first
            cached_results = await cache.get_search_results_with_depth(query, "serper", search_depth)
            if cached_results:
                print(f"✅ Cache hit for query: {query} (depth: {search_depth})")
                return cached_results
            
            url = "https://google.serper.dev/search"
            
            # Use global search depth configuration
            config = SEARCH_DEPTH_CONFIGS.get(search_depth, SEARCH_DEPTH_CONFIGS["standard"])
            num_results = config["num_results"]
            
            payload = json.dumps({
                "q": query,
                "num": num_results
            })
            
            headers = {
                'X-API-KEY': SERPER_API_KEY,
                'Content-Type': 'application/json'
            }
            
            # Make the API call - same approach as multi_source_search_agent.py
            response = await asyncio.to_thread(
                requests.post, url, headers=headers, data=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                organic_results = data.get("organic", [])
                
                # Convert to text format for LLM processing
                search_text = ""
                for result in organic_results:
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    link = result.get("link", "")
                    if title or snippet:
                        search_text += f"Title: {title}\nSnippet: {snippet}\nSource URL: {link}\n\n"
                
                # Cache the results
                await cache.set_search_results_with_depth(query, "serper", search_text, search_depth, ttl=7200)
                return search_text
            else:
                return f"Error: HTTP {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"

def company_aggregator_agent(state: GTMState) -> GTMState:
    logger.info("🏢 COMPANY AGGREGATOR: Starting company extraction...")
    logger.info(f"📋 Research Goal: {state.research_goal}")
    logger.info(f"🔍 Search Strategies: {len(state.search_strategies_generated)}")
    logger.info(f"🎯 Search Depth: {state.search_depth}")
    
    if not state.search_strategies_generated:
        raise ValueError("Missing search strategies")

    if not SERPER_API_KEY:
        raise ValueError("SERPER_API_KEY not found in environment variables")

    async def run_all(sem: asyncio.Semaphore):
        tasks = [run_serper(q, sem, state.search_depth) for q in state.search_strategies_generated]
        return await asyncio.gather(*tasks)

    print("🔍 Running Serper and extracting companies using GPT-4o-mini...")
    
    # TIME SERPER API CALLS
    import time
    serper_start = time.time()
    
    # Create semaphore in the same loop context
    async def main():
        sem = asyncio.Semaphore(state.max_parallel_searches)
        return await run_all(sem)
    
    search_results = asyncio.run(main())
    
    serper_end = time.time()
    serper_duration = (serper_end - serper_start) * 1000
    print(f"⏱️  Serper API calls took: {serper_duration:.2f}ms ({serper_duration/1000:.2f}s)")

    extractor = LLMCompanyExtractor()
    extracted_companies = []
    seen_domains = set()

    # TIME LLM EXTRACTION
    llm_start = time.time()
    
    # Run LLM extractions asynchronously
    async def extract_companies_async():
        sem = asyncio.Semaphore(state.max_parallel_searches)  # Limit concurrent LLM calls
        
        # Use global search depth configuration
        config = SEARCH_DEPTH_CONFIGS.get(state.search_depth, SEARCH_DEPTH_CONFIGS["standard"])
        max_companies = config["max_companies"]
        
        logger.info(f"🎯 COMPANY AGGREGATOR: Targeting {config['description']}")
        
        async def extract_single_result(result):
            async with sem:
                if isinstance(result, str) and result.startswith("Error:"):
                    print(f"❌ Search error: {result}")
                    return []
                
                try:
                    # Use async LLM call for better performance
                    input_text = extractor.prompt.format(
                        search_result=result,
                        research_goal=state.research_goal
                    )
                    structured_response = await extractor.structured_llm.ainvoke(input_text)
                    companies = structured_response.companies
                    return companies
                except Exception as e:
                    print("❌ LLM failed to parse companies:", e)
                    return []

        # Run all extractions in parallel
        extraction_tasks = [extract_single_result(result) for result in search_results]
        all_extracted_companies = await asyncio.gather(*extraction_tasks)
        
        # Process results and deduplicate
        for companies in all_extracted_companies:
            for company in companies:
                if company.domain not in seen_domains:
                    seen_domains.add(company.domain)
                    extracted_companies.append(CompanyMeta(**company.dict()))
                    
                    # Stop if we've reached the company limit
                    if len(extracted_companies) >= max_companies:
                        logger.info(f"🎯 COMPANY AGGREGATOR: Reached company limit ({max_companies})")
                        break
            # Stop if we've reached the company limit
            if len(extracted_companies) >= max_companies:
                break

    # Run the async extraction
    asyncio.run(extract_companies_async())
    
    llm_end = time.time()
    llm_duration = (llm_end - llm_start) * 1000
    print(f"⏱️  LLM extraction took: {llm_duration:.2f}ms ({llm_duration/1000:.2f}s)")
    
    # NEW: NEWS-BASED EXTRACTION
    print("📰 Starting news-based company extraction...")
    news_start = time.time()
    
    async def extract_news_companies():
        try:
            # Get news URLs for search strategies
            news_urls = await get_news_urls_for_queries(
                state.search_strategies_generated, 
                max_parallel=state.max_parallel_searches
            )
            
            # Use global search depth configuration
            config = SEARCH_DEPTH_CONFIGS.get(state.search_depth, SEARCH_DEPTH_CONFIGS["standard"])
            max_companies = config["max_companies"]
            
            if news_urls:
                # Extract companies from news articles
                news_companies = await extract_companies_from_news_urls(
                    news_urls, 
                    state.research_goal,
                    max_parallel=state.max_parallel_searches  # Limit parallel scraping
                )
                
                # Add news companies to existing list (avoiding duplicates)
                for company in news_companies:
                    if company.domain not in seen_domains:
                        seen_domains.add(company.domain)
                        extracted_companies.append(CompanyMeta(**company.dict()))
                        
                        # Stop if we've reached the company limit
                        if len(extracted_companies) >= max_companies:
                            logger.info(f"🎯 COMPANY AGGREGATOR: Reached company limit ({max_companies})")
                            break
                
                print(f"📰 Added {len(news_companies)} companies from news articles")
            else:
                print("📰 No news URLs found")
                
        except Exception as e:
            print(f"❌ News extraction failed: {e}")
    
    # Run the async news extraction
    asyncio.run(extract_news_companies())
    
    news_end = time.time()
    news_duration = (news_end - news_start) * 1000
    print(f"⏱️  News extraction took: {news_duration:.2f}ms ({news_duration/1000:.2f}s)")
    
    total_duration = (news_end - serper_start) * 1000
    print(f"⏱️  Total time: {total_duration:.2f}ms ({total_duration/1000:.2f}s)")

    # ✅ Save to disk for debugging
    os.makedirs("debug_output", exist_ok=True)
    output_path = os.path.join("debug_output", "extracted_companies.json")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([c.dict() for c in extracted_companies], f, ensure_ascii=False, indent=2)
        print(f"📁 Saved extracted companies to {output_path}")
    except Exception as e:
        print(f"⚠️ Failed to write extracted companies: {e}")

    return state.model_copy(update={"extracted_companies": extracted_companies})
