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

load_dotenv()

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
Return a list of companies with:
- Company name
- Domain (e.g., stripe.com)
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
    if not state.search_strategies_generated:
        raise ValueError("Missing search strategies")

    if not SERPER_API_KEY:
        raise ValueError("SERPER_API_KEY not found in environment variables")

    async def run_all(sem: asyncio.Semaphore):
        tasks = [run_serper(q, sem) for q in state.search_strategies_generated]
        return await asyncio.gather(*tasks)

    print("🔍 Running Serper and extracting companies using GPT-4o-mini...")
    
    # Create semaphore in the same loop context
    async def main():
        sem = asyncio.Semaphore(state.max_parallel_searches)
        return await run_all(sem)
    
    search_results = asyncio.run(main())

    extractor = LLMCompanyExtractor()
    extracted_companies = []
    seen_domains = set()

    # Run LLM extractions asynchronously
    async def extract_companies_async():
        sem = asyncio.Semaphore(state.max_parallel_searches)  # Limit concurrent LLM calls
        
        async def extract_single_result(result):
            async with sem:
                if isinstance(result, str) and result.startswith("Error:"):
                    print(f"❌ Search error: {result}")
                    return []
                
                try:
                    companies = extractor.extract(result, state.research_goal)
                    # print(f"📊 Extracted {len(companies)} companies from search result")
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
