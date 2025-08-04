import uvicorn
import time
import sys
import os
import asyncio
import json
from datetime import datetime
import io
import contextlib

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


from graph.gtm_graph import build_gtm_graph
from graph.state import GTMState



app = FastAPI(title="GTM Intelligence API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    research_goal: str
    search_depth: str = "standard"
    max_parallel_searches: int = 200
    confidence_threshold: float = 0.8
    max_iterations: int = 1

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

# Global variable to store the latest logs
latest_logs = []
log_callbacks = []

def add_log_callback(callback):
    """Add a callback function to be called when new logs are added"""
    log_callbacks.append(callback)

def log_message(message: str, level: str = "info"):
    """Add a log message and notify all callbacks"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "message": message
    }
    latest_logs.append(log_entry)
    
    # Keep only last 100 logs to prevent memory issues
    if len(latest_logs) > 100:
        latest_logs.pop(0)
    
    # Notify all callbacks
    for callback in log_callbacks:
        try:
            callback(log_entry)
        except Exception as e:
            print(f"Error in log callback: {e}")

# Custom stdout capture for agent logs with real-time streaming
class LogCapture:
    def __init__(self, log_callback):
        self.original_stdout = sys.stdout
        self.log_callback = log_callback
        self.buffer = ""
    
    def write(self, text):
        self.original_stdout.write(text)
        self.buffer += text
        
        # Send complete lines
        if '\n' in text:
            lines = self.buffer.split('\n')
            self.buffer = lines[-1]  # Keep incomplete line
            
            for line in lines[:-1]:
                if line.strip():  # Only send non-empty lines
                    self.log_callback(line.strip())
    
    def flush(self):
        self.original_stdout.flush()
        if self.buffer.strip():
            self.log_callback(self.buffer.strip())
            self.buffer = ""

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/logs")
async def get_logs():
    """Get all current logs"""
    return {"logs": latest_logs}

@app.post("/research/stream")
async def start_research_stream(request: ResearchRequest):
    """Stream research results with real-time logs"""
    
    async def generate():
        try:
            # Clear previous logs
            global latest_logs
            latest_logs = []
            
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'message': 'Starting research...', 'timestamp': datetime.now().isoformat()})}\n\n"
            
            # Initialize the graph
            graph = build_gtm_graph()
            
            # Create initial state
            initial_state = GTMState(
                research_goal=request.research_goal,
                search_depth=request.search_depth,
                max_parallel_searches=request.max_parallel_searches,
                confidence_threshold=request.confidence_threshold,
                max_iterations=request.max_iterations
            )
            
            yield f"data: {json.dumps({'type': 'status', 'message': 'Graph initialized, starting execution...', 'timestamp': datetime.now().isoformat()})}\n\n"
            
            # Start timing
            start_time = time.time()
            
            # Create a queue for real-time log streaming
            import queue
            log_queue = queue.Queue()
            
            def stream_log(log_line):
                log_data = {
                    "type": "log",
                    "message": log_line,
                    "timestamp": datetime.now().isoformat()
                }
                log_queue.put(f"data: {json.dumps(log_data)}\n\n")
            
            # Create log capture with callback
            log_capture = LogCapture(stream_log)
            
            # Run the graph in a separate thread
            import concurrent.futures
            
            def run_graph():
                with contextlib.redirect_stdout(log_capture):
                    return graph.invoke(initial_state)
            
            # Start the graph in a thread pool
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_graph)
                
                # Stream logs as they come in
                while not future.done():
                    try:
                        # Check for new logs (non-blocking)
                        log_entry = log_queue.get_nowait()
                        yield log_entry
                    except queue.Empty:
                        # No logs yet, check if work is done
                        if future.done():
                            break
                        # Small delay to avoid busy waiting
                        time.sleep(0.1)
                
                # Get the final result
                final_state = future.result()
            
            # Yield any remaining logs
            while not log_queue.empty():
                yield log_queue.get_nowait()
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Extract results
            if isinstance(final_state, dict):
                extracted_companies = final_state.get("extracted_companies", [])
                final_findings = final_state.get("final_findings", [])
                quality_metrics = final_state.get("quality_metrics", {})
                search_strategies_generated = len(final_state.get("search_strategies_generated", []))
                total_searches = final_state.get("total_searches_executed", 0)
            else:
                extracted_companies = getattr(final_state, "extracted_companies", [])
                final_findings = getattr(final_state, "final_findings", [])
                quality_metrics = getattr(final_state, "quality_metrics", {})
                search_strategies_generated = len(getattr(final_state, "search_strategies_generated", []))
                total_searches = getattr(final_state, "total_searches_executed", 0)
            
            # Format results
            company_domains = [company.domain for company in extracted_companies] if extracted_companies else []
            
            # Format final findings for response
            formatted_results = []
            if final_findings:
                for finding in final_findings:
                    formatted_result = {
                        "domain": finding.domain,
                        "confidence_score": finding.confidence_score,
                        "evidence_sources": finding.evidence_sources,
                        "signals_found": finding.signals_found,
                        "findings": {
                            "goal_achieved": finding.findings.get("goal_achieved", False),
                            "technologies": finding.findings.get("technologies", []),
                            "evidences": finding.findings.get("evidences", [])
                        }
                    }
                    formatted_results.append(formatted_result)
            
            # Extract quality metrics for response
            quality_metrics_response = {
                "quality_score": quality_metrics.get("quality_score", 0),
                "coverage_score": quality_metrics.get("coverage_score", 0),
                "missing_aspects": quality_metrics.get("missing_aspects", []),
                "coverage_gaps": quality_metrics.get("coverage_gaps", []),
                "evidence_issues": quality_metrics.get("evidence_issues", []),
                "recommendations": quality_metrics.get("recommendations", [])
            }
            
            # Search performance metrics
            search_performance = {
                "queries_per_second": round(total_searches / (processing_time_ms / 1000), 2) if processing_time_ms > 0 else 0,
                "cache_hit_rate": 0.0,  # Placeholder
                "failed_requests": 0     # Placeholder
            }
            
            # Clean and validate the response data
            def clean_for_json(obj):
                """Recursively clean objects for JSON serialization"""
                if isinstance(obj, dict):
                    return {k: clean_for_json(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [clean_for_json(item) for item in obj]
                elif isinstance(obj, str):
                    # Clean string for JSON
                    cleaned = obj.replace('\r', ' ').replace('\n', ' ')
                    cleaned = cleaned.replace('\\', '\\\\').replace('"', '\\"')
                    cleaned = cleaned.encode('utf-8', errors='ignore').decode('utf-8')
                    return cleaned[:5000] if len(cleaned) > 5000 else cleaned  # Limit length
                else:
                    return obj
            
            # Clean the response data
            cleaned_formatted_results = clean_for_json(formatted_results)
            cleaned_quality_metrics = clean_for_json(quality_metrics_response)
            
            # Send final results
            final_response = {
                "type": "results",
                "data": {
                    "research_goal": request.research_goal,
                    "search_depth": request.search_depth,
                    "total_companies": len(extracted_companies) if extracted_companies else 0,
                    "search_strategies_generated": search_strategies_generated,
                    "total_searches_executed": total_searches,
                    "processing_time_ms": processing_time_ms,
                    "company_domains": company_domains,
                    "results": cleaned_formatted_results,
                    "quality_metrics": cleaned_quality_metrics,
                    "search_performance": search_performance,
                    "status": "completed"
                }
            }
            
            try:
                yield f"data: {json.dumps(final_response, ensure_ascii=False)}\n\n"
            except Exception as json_error:
                # Fallback with minimal data
                fallback_response = {
                    "type": "results",
                    "data": {
                        "research_goal": request.research_goal,
                        "search_depth": request.search_depth,
                        "total_companies": len(extracted_companies) if extracted_companies else 0,
                        "search_strategies_generated": search_strategies_generated,
                        "total_searches_executed": total_searches,
                        "processing_time_ms": processing_time_ms,
                        "company_domains": company_domains,
                        "results": [],
                        "quality_metrics": {},
                        "search_performance": search_performance,
                        "status": "completed",
                        "error": "JSON serialization issue - results saved to debug files"
                    }
                }
                yield f"data: {json.dumps(fallback_response, ensure_ascii=False)}\n\n"
            
            # Send completion message
            yield f"data: {json.dumps({'type': 'complete', 'message': 'Research completed successfully', 'timestamp': datetime.now().isoformat()})}\n\n"
            
        except Exception as e:
            error_response = {
                "type": "error",
                "message": f"Research failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_response)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

@app.post("/research")
async def start_research(request: ResearchRequest):
    """Synchronous research endpoint (existing functionality)"""
    
    try:
        # Initialize the graph
        graph = build_gtm_graph()
        
        # Create initial state
        initial_state = GTMState(
            research_goal=request.research_goal,
            search_depth=request.search_depth,
            max_parallel_searches=request.max_parallel_searches,
            confidence_threshold=request.confidence_threshold,
            max_iterations=request.max_iterations
        )
        
        # Start timing
        start_time = time.time()
        
        # Run the graph in a thread to avoid event loop conflicts
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(graph.invoke, initial_state)
            final_state = future.result()
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Extract results
        if isinstance(final_state, dict):
            extracted_companies = final_state.get("extracted_companies", [])
            final_findings = final_state.get("final_findings", [])
            quality_metrics = final_state.get("quality_metrics", {})
            search_strategies_generated = len(final_state.get("search_strategies_generated", []))
            total_searches = final_state.get("total_searches_executed", 0)
        else:
            extracted_companies = getattr(final_state, "extracted_companies", [])
            final_findings = getattr(final_state, "final_findings", [])
            quality_metrics = getattr(final_state, "quality_metrics", {})
            search_strategies_generated = len(getattr(final_state, "search_strategies_generated", []))
            total_searches = getattr(final_state, "total_searches_executed", 0)
        
        # Format results
        company_domains = [company.domain for company in extracted_companies] if extracted_companies else []
        
        # Format final findings for response
        formatted_results = []
        if final_findings:
            for finding in final_findings:
                formatted_result = {
                    "domain": finding.domain,
                    "confidence_score": finding.confidence_score,
                    "evidence_sources": finding.evidence_sources,
                    "signals_found": finding.signals_found,
                    "findings": {
                        "goal_achieved": finding.findings.get("goal_achieved", False),
                        "technologies": finding.findings.get("technologies", []),
                        "evidences": finding.findings.get("evidences", [])
                    }
                }
                formatted_results.append(formatted_result)
        
        # Extract quality metrics for response
        quality_metrics_response = {
            "quality_score": quality_metrics.get("quality_score", 0),
            "coverage_score": quality_metrics.get("coverage_score", 0),
            "missing_aspects": quality_metrics.get("missing_aspects", []),
            "coverage_gaps": quality_metrics.get("coverage_gaps", []),
            "evidence_issues": quality_metrics.get("evidence_issues", []),
            "recommendations": quality_metrics.get("recommendations", [])
        }
        
        # Search performance metrics
        search_performance = {
            "queries_per_second": round(total_searches / (processing_time_ms / 1000), 2) if processing_time_ms > 0 else 0,
            "cache_hit_rate": 0.0,  # Placeholder
            "failed_requests": 0     # Placeholder
        }
        
        # Print results for debugging
        print(f"🎯 Search Depth: {request.search_depth}")
        print(f"📈 Quality Score: {quality_metrics_response['quality_score']:.2f}")
        print(f"📈 Coverage Score: {quality_metrics_response['coverage_score']:.2f}")
        print(f"🏢 Companies Found: {len(extracted_companies) if extracted_companies else 0}")
        print(f"⏱️ Processing Time: {processing_time_ms}ms")
        
        return ResearchResponse(
            research_goal=request.research_goal,
            search_depth=request.search_depth,
            total_companies=len(extracted_companies) if extracted_companies else 0,
            search_strategies_generated=search_strategies_generated,
            total_searches_executed=total_searches,
            processing_time_ms=processing_time_ms,
            company_domains=company_domains,
            results=formatted_results,
            quality_metrics=quality_metrics_response,
            search_performance=search_performance,
            status="completed"
        )
        
    except Exception as e:
        print(f"Research failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app.simple_api:app", host="0.0.0.0", port=8001, reload=True) 