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
You are an expert search query builder for GTM research. Your task is to generate 3-5 highly targeted search queries for finding evidence about a specific company about a research goal.
Remember to add the company name in the queries for a company targeted search.

Company Information:
- Name: {company_name}
- Domain: {domain}

Research Goal: {research_goal}

{company_feedback}

Instructions:
1. Generate 3-5 search queries that will find the most relevant evidence
2. Use specific, targeted terms that match the research goal
3. Include both company-specific and domain-specific variations
4. Use advanced search operators when helpful (site:, "quotes", AND, OR, etc.)
5. Focus on finding concrete evidence, not just general information
6. Ensure queries are diverse in their approach (case studies, technical details, user reviews, etc.)
7. If quality feedback is available, prioritize queries that address the specific gaps and issues identified

Return a structured response with:
- queries: List of 3-5 search queries with company name in the queries
- reasoning: Brief explanation of your query strategy
- search_focus: Primary focus area for these queries
""")

    async def build_queries_async(self, company_name: str, domain: str, research_goal: str, quality_metrics: dict = None) -> List[str]:
        """Build queries asynchronously using ainvoke with quality feedback"""
        
        # Get company-specific quality feedback
        company_feedback = ""
        if quality_metrics and 'company_analyses' in quality_metrics:
            company_analyses = quality_metrics['company_analyses']
            # Find analysis for this specific company
            for analysis in company_analyses:
                if analysis.get('company_domain') == domain:
                    quality_score = analysis.get('quality_score', 0)
                    coverage_score = analysis.get('coverage_score', 0)
                    gaps = analysis.get('gaps', [])
                    evidence_issues = analysis.get('evidence_issues', [])
                    recommendations = analysis.get('recommendations', [])
                    
                    # Convert lists to readable format
                    gaps_text = "\n".join([f"- {gap}" for gap in gaps[:3]]) if gaps else "None identified"
                    issues_text = "\n".join([f"- {issue}" for issue in evidence_issues[:3]]) if evidence_issues else "None identified"
                    recs_text = "\n".join([f"- {rec}" for rec in recommendations[:3]]) if recommendations else "None provided"
                    
                    company_feedback = f"""

PREVIOUS RESEARCH QUALITY FOR THIS COMPANY:
Quality Score: {quality_score:.2f}/1.0
Coverage Score: {coverage_score:.2f}/1.0

SPECIFIC GAPS FOR THIS COMPANY:
{gaps_text}

EVIDENCE ISSUES FOR THIS COMPANY:
{issues_text}

RECOMMENDATIONS FOR THIS COMPANY:
{recs_text}

IMPORTANT: Use this feedback to generate more targeted queries that address the specific gaps and issues for this company.
"""
                    break
        
        prompt_input = {
            "company_name": company_name,
            "domain": domain,
            "research_goal": research_goal,
            "company_feedback": company_feedback
        }
        
        try:
            structured_response = await self.structured_llm.ainvoke(self.prompt.format(**prompt_input))
            queries = structured_response.queries
            
            if not queries:
                queries = [f"{company_name} {research_goal}", f"{domain} {research_goal}", f"{company_name} site:{domain} {research_goal}"]
            
            # Enhance queries: ensure company name is included if not present
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
            
            # print(f"🤖 LLM generated {len(enhanced_queries)} queries for {company_name}")
            # print(f"   Focus: {structured_response.search_focus}")
            # print(f"   Reasoning: {structured_response.reasoning}")
            # print(f"   Original Queries: {queries}")
            # print(f"   Enhanced Queries: {enhanced_queries}")
            
            return enhanced_queries[:5]
            
        except Exception as e:
            print(f"❌ LLM query generation failed for {company_name}: {e}")
            # Fallback queries always include company name
            fallback_queries = [
                f"{company_name} {research_goal}", 
                f"{domain} {research_goal}", 
                f"{company_name} site:{domain} {research_goal}",
                f"{company_name} company {research_goal}",
                f"{company_name} technology {research_goal}"
            ]
            return fallback_queries[:5]

# Initialize the LLM query builder
llm_query_builder = LLMQueryBuilder()

async def run_serper(query: str, sem: asyncio.Semaphore):
    """Run Serper search with connection pooling"""
    async with sem:
        try:
            # Use connection pooling for API call
            response = await _make_serper_request(query)
            return query, response
            
        except Exception as e:
            # print(f"❌ Serper search failed for '{query}': {e}")
            return query, []

async def _make_serper_request(query: str) -> List[str]:
    """Make Serper API request using requests"""
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": 20}
    
    # Use asyncio.to_thread for synchronous requests - same as company_aggregator_agent
    response = await asyncio.to_thread(
        requests.post, url, headers=headers, json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        return [item.get("snippet", "") for item in data.get("organic", [])]
    else:
        raise Exception(f"Serper API error: {response.status_code}")

def multi_source_search_agent(state: GTMState) -> GTMState:
    if not state.extracted_companies:
        raise ValueError("No extracted companies to search")

    if not SERPER_API_KEY:
        raise ValueError("SERPER_API_KEY not found in environment variables")

    search_goal = state.research_goal
    
    # Check if we have quality metrics for feedback
    quality_metrics = state.quality_metrics or {}
    if quality_metrics:
        print(f"🎯 Using quality metrics feedback for targeted searches")
    else:
        print(f"📝 Using default search strategies")

    # TIME QUERY GENERATION
    import time
    query_start = time.time()
    total_start = time.time()

    async def generate_queries():
        """Generate queries for all companies using async LLM calls"""
        print(f"🔍 Building queries for {len(state.extracted_companies)} companies...")
        
        # Create semaphore for concurrent LLM calls
        sem = asyncio.Semaphore(state.max_parallel_searches)
        
        async def generate_queries_for_company(company):
            """Generate queries for a single company using async LLM"""
            async with sem:
                try:
                    queries = await llm_query_builder.build_queries_async(company.name, company.domain, search_goal, state.quality_metrics)
                    # print(f"  📝 {company.name} ({company.domain}): {queries}")
                    return queries
                except Exception as e:
                    print(f"❌ LLM failed to generate queries for {company.name}: {e}")
                    # Fallback to simple queries
                    return [f"{company.name} {search_goal}", f"{company.domain} {search_goal}"]
        
        # Run all query generations in parallel
        query_tasks = [generate_queries_for_company(company) for company in state.extracted_companies]
        all_company_queries = await asyncio.gather(*query_tasks)
        
        # Flatten the results
        all_queries = []
        for queries in all_company_queries:
            all_queries.extend(queries)
        
        return all_queries

    async def run_serper_searches(queries):
        """Run Serper API calls for all queries"""
        sem = asyncio.Semaphore(state.max_parallel_searches)
        tasks = [run_serper(query, sem) for query in queries]
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
                # print(f"  ✅ Matched query '{query}' to {matched_company.domain} got {len(result)} results")
                search_results_serper.setdefault(matched_company.domain, []).extend(result)
            else:
                # Fallback: try to extract domain from query or use a default
                print(f"⚠️ Could not match query '{query}' to any company domain")
                # Add to a general bucket to avoid losing data
                search_results_serper.setdefault("unknown", []).extend(result)

        return search_results_serper

    # Generate queries
    queries = asyncio.run(generate_queries())
    
    query_end = time.time()
    query_duration = (query_end - query_start) * 1000
    print(f"⏱️  Query generation took: {query_duration:.2f}ms ({query_duration/1000:.2f}s)")

    # TIME SERPER API CALLS
    serper_start = time.time()
    
    print("🔎 Running multi-source search for companies...")
    serper_results = asyncio.run(run_serper_searches(queries))
    
    serper_end = time.time()
    serper_duration = (serper_end - serper_start) * 1000
    print(f"⏱️  Serper API calls took: {serper_duration:.2f}ms ({serper_duration/1000:.2f}s)")
    
    total_end = time.time()
    total_duration = (total_end - total_start) * 1000
    print(f"⏱️  Total multi-source search time: {total_duration:.2f}ms ({total_duration/1000:.2f}s)")

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
