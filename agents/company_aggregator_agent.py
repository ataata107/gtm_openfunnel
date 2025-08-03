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

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

class ExtractedCompany(BaseModel):
    name: str = Field(..., description="Company name")
    domain: str = Field(..., description="Company domain (e.g., stripe.com)")
    source_url: str = Field(..., description="The URL where the company was found")

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

Given the following raw text from a search engine result, extract all **unique companies** that match the research goal.

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
- The source URL where it was mentioned

Only return a list of Pydantic models with the fields: name, domain, source_url.

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

async def run_serper(query: str, sem: asyncio.Semaphore):
    async with sem:
        try:
            url = "https://google.serper.dev/search"
            
            payload = json.dumps({
                "q": query,
                "num": 20
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
                
                return search_text
            else:
                return f"Error: HTTP {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"

def company_aggregator_agent(state: GTMState) -> GTMState:
    logger.info("🏢 COMPANY AGGREGATOR: Starting company extraction...")
    logger.info(f"📋 Research Goal: {state.research_goal}")
    logger.info(f"🔍 Search Strategies: {len(state.search_strategies_generated)}")
    
    if not state.search_strategies_generated:
        raise ValueError("Missing search strategies")

    if not SERPER_API_KEY:
        raise ValueError("SERPER_API_KEY not found in environment variables")

    async def run_all(sem: asyncio.Semaphore):
        tasks = [run_serper(q, sem) for q in state.search_strategies_generated]
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

    # Run the async extraction
    asyncio.run(extract_companies_async())
    
    llm_end = time.time()
    llm_duration = (llm_end - llm_start) * 1000
    print(f"⏱️  LLM extraction took: {llm_duration:.2f}ms ({llm_duration/1000:.2f}s)")
    
    total_duration = (llm_end - serper_start) * 1000
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
