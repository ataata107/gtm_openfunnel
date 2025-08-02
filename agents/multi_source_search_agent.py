# agents/multi_source_search_agent.py

import asyncio
import os
import json
import requests
from typing import List, Dict, Any
from graph.state import GTMState
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from utils.connection_pool import connection_pool

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Structured output for search queries
class SearchQueriesOutput(BaseModel):
    queries: List[str] = Field(..., description="List of 3-5 highly targeted search queries for finding evidence about the company")
    reasoning: str = Field(..., description="Brief explanation of why these queries were chosen")
    search_focus: str = Field(..., description="Primary focus area for these queries (e.g., 'case studies', 'technical details', 'user reviews')")

# LLM-based query builder with structured output
class LLMQueryBuilder:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        self.structured_llm = self.llm.with_structured_output(SearchQueriesOutput)
        self.prompt = PromptTemplate.from_template("""
You are an expert search query builder for GTM research. Your task is to generate 3-5 highly targeted search queries for finding evidence about a specific company.

Company Information:
- Name: {company_name}
- Domain: {domain}

Research Goal: {research_goal}

Available Refined Strategies (if any):
{refined_strategies_text}

Instructions:
1. Generate 3-5 search queries that will find the most relevant evidence
2. Use specific, targeted terms that match the research goal
3. If refined strategies are available, incorporate their insights
4. Include both company-specific and domain-specific variations
5. Use advanced search operators when helpful (site:, "quotes", AND, OR, etc.)
6. Focus on finding concrete evidence, not just general information
7. Ensure queries are diverse in their approach (case studies, technical details, user reviews, etc.)

Return a structured response with:
- queries: List of 3-5 search queries
- reasoning: Brief explanation of your query strategy
- search_focus: Primary focus area for these queries
""")

    def build_queries(self, company_name: str, domain: str, research_goal: str, refined_strategies: list = None) -> List[str]:
        """Build queries synchronously to avoid asyncio issues"""
        refined_strategies_text = "None available"
        if refined_strategies:
            strategy_texts = []
            for i, strategy in enumerate(refined_strategies[:3]):
                strategy_type = strategy.get('strategy_type', 'unknown')
                queries = strategy.get('search_queries', [])
                reasoning = strategy.get('reasoning', '')
                strategy_texts.append(f"Strategy {i+1} ({strategy_type}): {queries[:2]} - {reasoning[:100]}...")
            refined_strategies_text = "\n".join(strategy_texts)
        
        prompt_input = {
            "company_name": company_name,
            "domain": domain,
            "research_goal": research_goal,
            "refined_strategies_text": refined_strategies_text
        }
        
        try:
            structured_response = self.structured_llm.invoke(self.prompt.format(**prompt_input))
            queries = structured_response.queries
            
            if not queries:
                queries = [f"{company_name} {research_goal}", f"{domain} {research_goal}", f"{company_name} site:{domain} {research_goal}"]
            
            # print(f"🤖 LLM generated {len(queries)} queries for {company_name}")
            # print(f"   Focus: {structured_response.search_focus}")
            # print(f"   Reasoning: {structured_response.reasoning}")
            # print(f"   Queries: {queries}")
            
            return queries[:5]
            
        except Exception as e:
            print(f"❌ LLM query generation failed for {company_name}: {e}")
            return [f"{company_name} {research_goal}", f"{domain} {research_goal}", f"{company_name} site:{domain} {research_goal}"]

# Initialize the LLM query builder
llm_query_builder = LLMQueryBuilder()

def build_queries(company_name: str, domain: str, research_goal: str, refined_strategies: list = None) -> list:
    """Build search queries for a company using LLM for intelligent query generation with structured output"""
    return llm_query_builder.build_queries(company_name, domain, research_goal, refined_strategies)

async def run_serper(query: str, sem: asyncio.Semaphore):
    """Run Serper search with connection pooling"""
    async with sem:
        try:
            # Use connection pooling for API call
            response = await _make_serper_request(query)
            return query, response
            
        except Exception as e:
            print(f"❌ Serper search failed for '{query}': {e}")
            return query, []

async def _make_serper_request(query: str) -> List[str]:
    """Make Serper API request using requests"""
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": 10}
    
    # Use asyncio.to_thread for synchronous requests
    def make_request():
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            return [item.get("snippet", "") for item in data.get("organic", [])]
        else:
            raise Exception(f"Serper API error: {response.status_code}")
    
    return await asyncio.to_thread(make_request)

def multi_source_search_agent(state: GTMState) -> GTMState:
    if not state.extracted_companies:
        raise ValueError("No extracted companies to search")

    if not SERPER_API_KEY:
        raise ValueError("SERPER_API_KEY not found in environment variables")

    search_goal = state.research_goal
    
    # Check if we have refined strategies from strategy refinement agent
    strategy_refinement = state.strategy_refinement or {}
    refined_strategies = strategy_refinement.get('refined_strategies', [])
    
    if refined_strategies:
        print(f"🎯 Using {len(refined_strategies)} refined strategies for targeted searches")
    else:
        print(f"📝 Using default search strategies")

    async def run_all():
        sem = asyncio.Semaphore(state.max_parallel_searches)
        tasks = []

        print(f"🔍 Building queries for {len(state.extracted_companies)} companies...")
        for company in state.extracted_companies:
            queries = build_queries(company.name, company.domain, search_goal, refined_strategies)
            print(f"  📝 {company.name} ({company.domain}): {queries}")
            for query in queries:
                tasks.append(run_serper(query, sem))

        results = await asyncio.gather(*tasks)

        # ✅ Write to serper-specific field
        search_results_serper = dict(state.search_results_serper or {})
        print(f"📊 Processing {len(results)} search results...")
        for query, result in results:
            # Find which company this query belongs to
            matched_company = None
            for company in state.extracted_companies:
                # Check if this query was generated for this company
                if (company.name in query or company.domain in query):
                    matched_company = company
                    break
            
            if matched_company:
                print(f"  ✅ Matched query '{query}' to {matched_company.domain} got {len(result)} results")
                search_results_serper.setdefault(matched_company.domain, []).extend(result)
            else:
                # Fallback: try to extract domain from query or use a default
                print(f"⚠️ Could not match query '{query}' to any company domain")
                # Add to a general bucket to avoid losing data
                search_results_serper.setdefault("unknown", []).extend(result)

        return search_results_serper

    print("🔎 Running multi-source search for companies...")
    serper_results = asyncio.run(run_all())

    # ✅ Save to disk for debugging
    os.makedirs("debug_output", exist_ok=True)
    output_path = os.path.join("debug_output", "serper_search_output.json")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(serper_results, f, ensure_ascii=False, indent=2)
        print(f"📁 Saved Serper search results to {output_path}")
    except Exception as e:
        print(f"⚠️ Failed to write Serper search results: {e}")

    # Increment iteration count for feedback loop tracking
    new_iteration_count = state.iteration_count + 1
    print(f"📊 Research Iteration: {new_iteration_count}/{state.max_iterations}")

    return state.model_copy(update={
        "search_results_serper": serper_results,
        "iteration_count": new_iteration_count
    })
