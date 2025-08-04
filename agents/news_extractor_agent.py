# agents/news_extractor_agent.py

import asyncio
import os
import json
from typing import List
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from graph.state import ExtractedCompany
from dotenv import load_dotenv
import logging
import nest_asyncio
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser

load_dotenv()
nest_asyncio.apply()

# Configure logging
logger = logging.getLogger(__name__)

class CompanyExtractionOutput(BaseModel):
    companies: List[ExtractedCompany]

# Global LLM setup (browser will be created per function call)
llm = ChatOpenAI(model="gpt-4o-mini")

async def extract_companies_from_news_urls(news_urls: List[str], research_goal: str, max_parallel: int = 3) -> List[ExtractedCompany]:
    """Extract companies from multiple news URLs using simple LLM with tools binding"""
    all_companies = []
    seen_domains = set()
    
    # Create browser and tools within the function scope
    async_browser = create_async_playwright_browser(headless=True)
    toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
    all_tools = toolkit.get_tools()
    
    llm_with_tools = llm.bind_tools(all_tools)
    llm_with_output = llm.with_structured_output(CompanyExtractionOutput)
    
    try:
        # Process URLs in batches
        sem = asyncio.Semaphore(max_parallel)
        
        async def process_single_url(url: str):
            async with sem:
                try:
                    # Simple message to the LLM with tools
                    message = f"""
                    Please visit {url} and extract all companies relevant to this research goal: {research_goal}
                    
                    Return a list of companies with name and domain you are able to find for certainity. Focus on companies that match the research objective only.
                    """
                    
                    # Let the LLM use the browser tools directly
                    response = await llm_with_output.ainvoke(message)
                    companies = response.companies
                    
                    # Filter out duplicates
                    unique_companies = []
                    for company in companies:
                        if company.domain not in seen_domains:
                            unique_companies.append(company)
                            seen_domains.add(company.domain)
                    
                    print(f"📰 Extracted {len(unique_companies)} companies from {url}")
                    return unique_companies
                    
                except Exception as e:
                    print(f"❌ Failed to process {url}: {e}")
                    return []
        
        # Process all URLs
        tasks = [process_single_url(url) for url in news_urls]
        results = await asyncio.gather(*tasks)
        
        # Combine all results
        for companies in results:
            all_companies.extend(companies)
        
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