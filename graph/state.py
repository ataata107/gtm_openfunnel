from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Annotated, Any


class CompanyMeta(BaseModel):
    name: str = Field(..., description="Company name extracted from search results")
    domain: str = Field(..., description="Company's primary domain or website")
    source_url: Optional[str] = Field(None, description="URL where the company was found")


class CompanyFinding(BaseModel):
    domain: str = Field(..., description="Company domain (e.g., stripe.com)")
    confidence_score: float = Field(..., description="Score for how well the data supports the research goal")
    evidence_sources: int = Field(..., description="Number of raw evidence snippets collected")
    findings: Dict[str, Any] = Field(..., description="Structured insights extracted about the company")
    signals_found: int = Field(..., description="Number of distinct signals found")


class PerformanceStats(BaseModel):
    queries_per_second: float = Field(..., description="Throughput of search agent")
    failed_requests: int = Field(..., description="Number of failed or error responses during search")
    cache_hit_rate: Optional[float] = Field(None, description="Optional: How many results came from cache")


class GTMState(BaseModel):
    research_goal: Annotated[str, "union"] = Field(..., description="High-level goal of the research (e.g., 'Find fintech companies using AI for fraud detection')")
    search_depth: str = Field(default="standard", description="Depth of search to perform: quick | standard | comprehensive")
    max_parallel_searches: int = Field(default=20, description="Number of parallel search executions allowed")
    confidence_threshold: float = Field(default=0.8, description="Minimum acceptable confidence to proceed with aggregation")

    search_strategies_generated: Optional[List[str]] = Field(default=None, description="LLM-generated search strategies for web research")
    extracted_companies: Optional[List[CompanyMeta]] = Field(default=None, description="List of unique companies extracted from search results")

    # ✅ Parallel-update-safe fields for concurrent agents
    search_results_serper: Optional[Annotated[Dict[str, List[str]], "union"]] = Field(default=None, description="Domain → Serper search result snippets")
    search_results_website: Optional[Annotated[Dict[str, List[str]], "union"]] = Field(default=None, description="Domain → Raw HTML or text scraped from website")
    search_results_jobboard: Optional[Annotated[Dict[str, List[str]], "union"]] = Field(default=None, description="Domain → Job board posting content")
    search_results_news: Optional[Annotated[Dict[str, List[str]], "union"]] = Field(default=None, description="Domain → News/PR mentions")

    # # 🔄 Final merged evidence corpus for evaluation
    # search_results: Optional[Dict[str, List[str]]] = Field(default=None, description="Domain → Combined evidence text from all sources")

    # Evaluation results
    final_findings: List[CompanyFinding] = Field(default_factory=list)
    
    # Quality analysis results
    quality_metrics: Dict[str, Any] = Field(default_factory=dict, description="Quality analysis metrics and gaps")
    
    # Strategy refinement results
    strategy_refinement: Dict[str, Any] = Field(default_factory=dict, description="Strategy refinement results and new queries")

    # Iteration tracking for feedback loops
    iteration_count: int = Field(default=0, description="Number of research iterations completed")
    max_iterations: int = Field(default=3, description="Maximum number of research iterations allowed")

    performance: Optional[PerformanceStats] = Field(default=None, description="Stats for performance and error metrics")
