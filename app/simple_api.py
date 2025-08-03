from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import time
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.gtm_graph import build_gtm_graph
from graph.state import GTMState

# Initialize FastAPI app
app = FastAPI(
    title="GTM Intelligence API - Simple",
    description="Simple synchronous API for GTM research",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class ResearchRequest(BaseModel):
    research_goal: str = Field(..., description="High-level goal of the research")
    search_depth: str = Field(default="quick", description="quick | standard | comprehensive")
    max_parallel_searches: int = Field(default=100, description="Number of parallel search executions")
    confidence_threshold: float = Field(default=0.8, description="Minimum acceptable confidence")
    max_iterations: int = Field(default=1, description="Maximum research iterations")

class ResearchResponse(BaseModel):
    research_goal: str
    search_depth: str
    total_companies: int
    search_strategies_generated: int
    total_searches_executed: int
    processing_time_ms: int
    company_domains: list
    results: list
    quality_metrics: dict
    search_performance: dict
    status: str

@app.post("/research", response_model=ResearchResponse)
def start_research(request: ResearchRequest):
    """Simple synchronous research endpoint"""
    try:
        start_time = time.time()
        
        print(f"🚀 Starting research: {request.research_goal}")
        
        # Build and execute GTM graph
        gtm_workflow = build_gtm_graph()
        
        # Create initial state
        initial_state = GTMState(
            research_goal=request.research_goal,
            search_depth=request.search_depth,
            max_parallel_searches=request.max_parallel_searches,
            confidence_threshold=request.confidence_threshold,
            max_iterations=request.max_iterations
        )
        
        print("🔄 Executing GTM workflow...")
        
        # Execute the workflow
        final_state = gtm_workflow.invoke(initial_state)
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Extract results
        if isinstance(final_state, dict):
            search_strategies = final_state.get("search_strategies_generated", [])
            companies = final_state.get("extracted_companies", [])
            findings = final_state.get("final_findings", [])
            performance = final_state.get("performance", {})
            quality_metrics = final_state.get("quality_metrics", {})
        else:
            search_strategies = getattr(final_state, "search_strategies_generated", [])
            companies = getattr(final_state, "extracted_companies", [])
            findings = getattr(final_state, "final_findings", [])
            performance = getattr(final_state, "performance", {})
            quality_metrics = getattr(final_state, "quality_metrics", {})
        
        # Calculate metrics
        total_companies = len(companies) if companies else 0
        search_strategies_count = len(search_strategies) if search_strategies else 0
        
        # Calculate total searches executed
        total_searches = 0
        if isinstance(final_state, dict):
            serper_results = final_state.get("search_results_serper", {})
            website_results = final_state.get("search_results_website", {})
        else:
            serper_results = getattr(final_state, "search_results_serper", {})
            website_results = getattr(final_state, "search_results_website", {})
        
        total_searches += sum(len(snippets) for snippets in serper_results.values())
        total_searches += sum(len(snippets) for snippets in website_results.values())
        
        # Extract company domains
        company_domains = [company.domain for company in companies] if companies else []
        
        # Format results
        formatted_results = []
        for finding in findings:
            formatted_result = {
                "domain": finding.domain,
                "confidence_score": finding.confidence_score,
                "evidence_sources": finding.evidence_sources,
                "findings": finding.findings,
                "signals_found": finding.signals_found
            }
            formatted_results.append(formatted_result)
        
        # Calculate performance metrics
        search_performance = {
            "queries_per_second": performance.get("queries_per_second", 0),
            "cache_hit_rate": performance.get("cache_hit_rate", 0),
            "failed_requests": performance.get("failed_requests", 0)
        }
        
        # Extract quality metrics
        quality_metrics_response = {
            "quality_score": quality_metrics.get("quality_score", 0),
            "coverage_score": quality_metrics.get("coverage_score", 0),
            "missing_aspects": quality_metrics.get("missing_aspects", []),
            "coverage_gaps": quality_metrics.get("coverage_gaps", []),
            "evidence_issues": quality_metrics.get("evidence_issues", []),
            "recommendations": quality_metrics.get("recommendations", [])
        }
        
        print(f"✅ Research completed in {processing_time_ms}ms")
        print(f"📊 Found {total_companies} companies, {search_strategies_count} strategies")
        print(f"🎯 Search Depth: {request.search_depth}")
        print(f"📈 Quality Score: {quality_metrics_response['quality_score']:.2f}")
        print(f"📈 Coverage Score: {quality_metrics_response['coverage_score']:.2f}")
        
        return ResearchResponse(
            research_goal=request.research_goal,
            search_depth=request.search_depth,
            total_companies=total_companies,
            search_strategies_generated=search_strategies_count,
            total_searches_executed=total_searches,
            processing_time_ms=processing_time_ms,
            company_domains=company_domains,
            results=formatted_results,
            quality_metrics=quality_metrics_response,
            search_performance=search_performance,
            status="completed"
        )
        
    except Exception as e:
        print(f"❌ Research failed: {e}")
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "GTM Intelligence API - Simple"
    }

# API documentation
@app.get("/")
def root():
    """API root with documentation links"""
    return {
        "message": "GTM Intelligence API - Simple",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "POST /research": "Start a research (synchronous)",
            "GET /health": "Health check"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 