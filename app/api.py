import uuid
import time
import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from graph.gtm_graph import build_gtm_graph
from graph.state import GTMState, CompanyFinding, PerformanceStats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GTM Intelligence API",
    description="Multi-Source GTM Research Engine with intelligent search query generation and parallel processing",
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

# In-memory storage for research sessions (in production, use Redis/Database)
research_sessions: Dict[str, Dict[str, Any]] = {}

# Pydantic models for API requests/responses
class ResearchRequest(BaseModel):
    research_goal: str = Field(..., description="High-level goal of the research")
    search_depth: str = Field(default="standard", description="quick | standard | comprehensive")
    max_parallel_searches: int = Field(default=20, description="Number of parallel search executions")
    confidence_threshold: float = Field(default=0.8, description="Minimum acceptable confidence")
    max_iterations: int = Field(default=3, description="Maximum research iterations")

class ResearchResponse(BaseModel):
    research_id: str
    status: str
    total_companies: int
    search_strategies_generated: int
    total_searches_executed: int
    processing_time_ms: int
    company_domains: List[str]
    results: List[Dict[str, Any]]
    search_performance: Dict[str, Any]
    created_at: str
    updated_at: str

class ResearchStatus(BaseModel):
    research_id: str
    status: str
    progress: float
    current_step: str
    estimated_completion: Optional[str]

# Background task to execute research
async def execute_research(research_id: str, request: ResearchRequest):
    """Execute research in background with detailed logging"""
    try:
        start_time = time.time()
        
        # Update session status
        research_sessions[research_id]["status"] = "processing"
        research_sessions[research_id]["current_step"] = "Initializing research workflow"
        logger.info(f"🚀 Starting research for {research_id}: {request.research_goal}")
        
        # Build and execute GTM graph
        logger.info("🔧 Building GTM graph...")
        gtm_workflow = build_gtm_graph()
        
        # Create initial state
        logger.info("📝 Creating initial state...")
        initial_state = GTMState(
            research_goal=request.research_goal,
            search_depth=request.search_depth,
            max_parallel_searches=request.max_parallel_searches,
            confidence_threshold=request.confidence_threshold,
            max_iterations=request.max_iterations
        )
        
        research_sessions[research_id]["current_step"] = "Executing research workflow"
        logger.info("🔄 Executing GTM workflow...")
        
        # Execute the workflow with detailed logging
        logger.info("=" * 60)
        logger.info("🎯 GTM RESEARCH WORKFLOW EXECUTION")
        logger.info("=" * 60)
        
        final_state = gtm_workflow.invoke(initial_state)
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        logger.info(f"⏱️ Total processing time: {processing_time_ms}ms")
        
        # Extract results
        if isinstance(final_state, dict):
            search_strategies = final_state.get("search_strategies_generated", [])
            companies = final_state.get("extracted_companies", [])
            findings = final_state.get("final_findings", [])
            performance = final_state.get("performance", {})
        else:
            search_strategies = getattr(final_state, "search_strategies_generated", [])
            companies = getattr(final_state, "extracted_companies", [])
            findings = getattr(final_state, "final_findings", [])
            performance = getattr(final_state, "performance", {})
        
        # Log detailed results
        logger.info("📊 RESEARCH RESULTS SUMMARY")
        logger.info("=" * 40)
        logger.info(f"🔍 Search Strategies Generated: {len(search_strategies) if search_strategies else 0}")
        logger.info(f"🏢 Companies Extracted: {len(companies) if companies else 0}")
        logger.info(f"📋 Final Findings: {len(findings) if findings else 0}")
        
        if companies:
            logger.info("🏢 Extracted Companies:")
            for company in companies:
                logger.info(f"   - {company.name} ({company.domain})")
        
        if findings:
            logger.info("📋 Company Findings:")
            for finding in findings:
                logger.info(f"   - {finding.domain}: {finding.confidence_score:.2f} confidence")
        
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
        
        logger.info(f"🔍 Total Searches Executed: {total_searches}")
        
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
        
        logger.info("📈 PERFORMANCE METRICS")
        logger.info("=" * 30)
        logger.info(f"⏱️ Processing Time: {processing_time_ms}ms")
        logger.info(f"🔍 Queries/Second: {search_performance['queries_per_second']}")
        logger.info(f"💾 Cache Hit Rate: {search_performance['cache_hit_rate']}")
        logger.info(f"❌ Failed Requests: {search_performance['failed_requests']}")
        
        # Update session with results
        research_sessions[research_id].update({
            "status": "completed",
            "total_companies": total_companies,
            "search_strategies_generated": search_strategies_count,
            "total_searches_executed": total_searches,
            "processing_time_ms": processing_time_ms,
            "company_domains": company_domains,
            "results": formatted_results,
            "search_performance": search_performance,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        logger.info("✅ Research completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Research failed: {str(e)}")
        logger.error(f"Error details: {type(e).__name__}: {e}")
        research_sessions[research_id].update({
            "status": "failed",
            "error": str(e),
            "updated_at": datetime.utcnow().isoformat()
        })

@app.post("/research/batch", response_model=ResearchResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Start a new research batch"""
    research_id = str(uuid.uuid4())
    
    logger.info(f"🚀 New research request: {research_id}")
    logger.info(f"📋 Research Goal: {request.research_goal}")
    logger.info(f"🔍 Search Depth: {request.search_depth}")
    logger.info(f"⚡ Max Parallel Searches: {request.max_parallel_searches}")
    logger.info(f"🎯 Confidence Threshold: {request.confidence_threshold}")
    
    # Initialize session
    research_sessions[research_id] = {
        "research_id": research_id,
        "status": "queued",
        "request": request.dict(),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "current_step": "Initializing",
        "progress": 0.0
    }
    
    # Start background task
    background_tasks.add_task(execute_research, research_id, request)
    
    # Return immediate response
    return ResearchResponse(
        research_id=research_id,
        status="queued",
        total_companies=0,
        search_strategies_generated=0,
        total_searches_executed=0,
        processing_time_ms=0,
        company_domains=[],
        results=[],
        search_performance={},
        created_at=research_sessions[research_id]["created_at"],
        updated_at=research_sessions[research_id]["updated_at"]
    )

@app.get("/research/{research_id}", response_model=ResearchResponse)
async def get_research_results(research_id: str):
    """Get research results by ID"""
    if research_id not in research_sessions:
        raise HTTPException(status_code=404, detail="Research not found")
    
    session = research_sessions[research_id]
    
    return ResearchResponse(
        research_id=session["research_id"],
        status=session["status"],
        total_companies=session.get("total_companies", 0),
        search_strategies_generated=session.get("search_strategies_generated", 0),
        total_searches_executed=session.get("total_searches_executed", 0),
        processing_time_ms=session.get("processing_time_ms", 0),
        company_domains=session.get("company_domains", []),
        results=session.get("results", []),
        search_performance=session.get("search_performance", {}),
        created_at=session["created_at"],
        updated_at=session["updated_at"]
    )

@app.get("/research/{research_id}/status", response_model=ResearchStatus)
async def get_research_status(research_id: str):
    """Get research status and progress"""
    if research_id not in research_sessions:
        raise HTTPException(status_code=404, detail="Research not found")
    
    session = research_sessions[research_id]
    
    # Calculate progress based on status
    progress = 0.0
    if session["status"] == "completed":
        progress = 100.0
    elif session["status"] == "processing":
        progress = 50.0  # Rough estimate
    elif session["status"] == "failed":
        progress = 0.0
    
    return ResearchStatus(
        research_id=session["research_id"],
        status=session["status"],
        progress=progress,
        current_step=session.get("current_step", "Unknown"),
        estimated_completion=None
    )

@app.get("/research")
async def list_research_sessions():
    """List all research sessions"""
    sessions = []
    for research_id, session in research_sessions.items():
        sessions.append({
            "research_id": research_id,
            "status": session["status"],
            "research_goal": session["request"]["research_goal"],
            "created_at": session["created_at"],
            "updated_at": session["updated_at"]
        })
    
    return {"sessions": sessions}

@app.delete("/research/{research_id}")
async def delete_research_session(research_id: str):
    """Delete a research session"""
    if research_id not in research_sessions:
        raise HTTPException(status_code=404, detail="Research not found")
    
    del research_sessions[research_id]
    return {"message": "Research session deleted successfully"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_sessions": len(research_sessions)
    }

# API documentation
@app.get("/")
async def root():
    """API root with documentation links"""
    return {
        "message": "GTM Intelligence API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "POST /research/batch": "Start a new research batch",
            "GET /research/{research_id}": "Get research results",
            "GET /research/{research_id}/status": "Get research status",
            "GET /research": "List all research sessions",
            "DELETE /research/{research_id}": "Delete research session",
            "GET /health": "Health check"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
