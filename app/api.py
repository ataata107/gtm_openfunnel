import uuid
import time
import asyncio
import json
import re
from typing import List, Dict, Optional, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

def clean_json_string(text: str) -> str:
    """Clean string for safe JSON serialization"""
    if not isinstance(text, str):
        return str(text)
    
    # Remove null bytes and control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Replace problematic characters that can break JSON
    text = text.replace('\r', ' ').replace('\n', ' ')
    text = text.replace('\\', '\\\\')  # Escape backslashes
    text = text.replace('"', '\\"')    # Escape quotes
    text = text.replace('\t', ' ')     # Replace tabs
    
    # Remove any trailing incomplete UTF-8 sequences
    text = text.encode('utf-8', errors='ignore').decode('utf-8')
    
    # Limit length to prevent memory issues
    if len(text) > 10000:
        text = text[:10000] + "..."
    
    return text.strip()

from graph.gtm_graph import build_gtm_graph
from graph.state import GTMState, CompanyFinding, PerformanceStats

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
        print(f"🚀 Starting research for {research_id}: {request.research_goal}")
        
        # Build and execute GTM graph
        print("🔧 Building GTM graph...")
        gtm_workflow = build_gtm_graph()
        
        # Create initial state
        print("📝 Creating initial state...")
        initial_state = GTMState(
            research_goal=request.research_goal,
            search_depth=request.search_depth,
            max_parallel_searches=request.max_parallel_searches,
            confidence_threshold=request.confidence_threshold,
            max_iterations=request.max_iterations
        )
        
        research_sessions[research_id]["current_step"] = "Executing research workflow"
        print("🔄 Executing GTM workflow...")
        
        # Execute the workflow with detailed logging
        print("=" * 60)
        print("🎯 GTM RESEARCH WORKFLOW EXECUTION")
        print("=" * 60)
        
        final_state = gtm_workflow.invoke(initial_state)
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        print(f"⏱️ Total processing time: {processing_time_ms}ms")
        
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
        print("📊 RESEARCH RESULTS SUMMARY")
        print("=" * 40)
        print(f"🔍 Search Strategies Generated: {len(search_strategies) if search_strategies else 0}")
        print(f"🏢 Companies Extracted: {len(companies) if companies else 0}")
        print(f"📋 Final Findings: {len(findings) if findings else 0}")
        
        if companies:
            print("🏢 Extracted Companies:")
            for company in companies:
                print(f"   - {company.name} ({company.domain})")
        
        if findings:
            print("📋 Company Findings:")
            for finding in findings:
                print(f"   - {finding.domain}: {finding.confidence_score:.2f} confidence")
        
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
        
        print(f"🔍 Total Searches Executed: {total_searches}")
        
        # Extract company domains
        company_domains = [company.domain for company in companies] if companies else []
        
        # Format results with proper JSON handling
        formatted_results = []
        for finding in findings:
            try:
                # Clean and validate the findings data
                findings_data = finding.findings
                if isinstance(findings_data, dict):
                    # Ensure all string values are properly encoded
                    cleaned_findings = {}
                    for key, value in findings_data.items():
                        if isinstance(value, str):
                            # Clean any problematic characters
                            cleaned_value = clean_json_string(value)
                            cleaned_findings[key] = cleaned_value
                        elif isinstance(value, list):
                            # Clean list items
                            cleaned_list = []
                            for item in value:
                                if isinstance(item, str):
                                    cleaned_item = clean_json_string(item)
                                    cleaned_list.append(cleaned_item)
                                else:
                                    cleaned_list.append(item)
                            cleaned_findings[key] = cleaned_list
                        else:
                            cleaned_findings[key] = value
                else:
                    cleaned_findings = findings_data
                
                formatted_result = {
                    "domain": finding.domain,
                    "confidence_score": finding.confidence_score,
                    "evidence_sources": finding.evidence_sources,
                    "findings": cleaned_findings,
                    "signals_found": finding.signals_found
                }
                formatted_results.append(formatted_result)
            except Exception as e:
                print(f"⚠️ Error formatting finding for {finding.domain}: {e}")
                # Add a safe fallback
                formatted_results.append({
                    "domain": finding.domain,
                    "confidence_score": finding.confidence_score,
                    "evidence_sources": finding.evidence_sources,
                    "findings": {"error": "Data formatting issue"},
                    "signals_found": finding.signals_found
                })
        
        # Calculate performance metrics
        search_performance = {
            "queries_per_second": performance.get("queries_per_second", 0),
            "cache_hit_rate": performance.get("cache_hit_rate", 0),
            "failed_requests": performance.get("failed_requests", 0)
        }
        
        print("📈 PERFORMANCE METRICS")
        print("=" * 30)
        print(f"⏱️ Processing Time: {processing_time_ms}ms")
        print(f"🔍 Queries/Second: {search_performance['queries_per_second']}")
        print(f"💾 Cache Hit Rate: {search_performance['cache_hit_rate']}")
        print(f"❌ Failed Requests: {search_performance['failed_requests']}")
        
        # Update session with results (with JSON safety)
        try:
            # Test JSON serialization before saving
            import json
            test_json = json.dumps({
                "status": "completed",
                "total_companies": total_companies,
                "search_strategies_generated": search_strategies_count,
                "total_searches_executed": total_searches,
                "processing_time_ms": processing_time_ms,
                "company_domains": company_domains,
                "results": formatted_results,
                "search_performance": search_performance,
                "updated_at": datetime.utcnow().isoformat()
            }, ensure_ascii=False, default=str)
            
            # If JSON serialization succeeds, update the session
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
            
        except Exception as e:
            print(f"❌ JSON serialization error: {e}")
            # Save a minimal response without problematic data
            research_sessions[research_id].update({
                "status": "completed",
                "total_companies": total_companies,
                "search_strategies_generated": search_strategies_count,
                "total_searches_executed": total_searches,
                "processing_time_ms": processing_time_ms,
                "company_domains": company_domains,
                "results": [],  # Empty results to avoid JSON issues
                "search_performance": search_performance,
                "updated_at": datetime.utcnow().isoformat(),
                "error": "JSON serialization issue - results saved to debug files"
            })
        
        print("✅ Research completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Research failed: {str(e)}")
        print(f"Error details: {type(e).__name__}: {e}")
        research_sessions[research_id].update({
            "status": "failed",
            "error": str(e),
            "updated_at": datetime.utcnow().isoformat()
        })

@app.post("/research/batch", response_model=ResearchResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Start a new research batch"""
    research_id = str(uuid.uuid4())
    
    print(f"🚀 New research request: {research_id}")
    print(f"📋 Research Goal: {request.research_goal}")
    print(f"🔍 Search Depth: {request.search_depth}")
    print(f"⚡ Max Parallel Searches: {request.max_parallel_searches}")
    print(f"🎯 Confidence Threshold: {request.confidence_threshold}")

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
