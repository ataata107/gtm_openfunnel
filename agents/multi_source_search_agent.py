# agents/multi_source_search_agent.py

import asyncio
import os
import json
from typing import List, Dict, Any
from graph.state import GTMState, CompanyFinding
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from utils.cache import cache
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.tools import Tool

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Structured output for evaluation
class EvaluationOutput(BaseModel):
    goal_achieved: bool = Field(..., description="Whether the company meets the research goal criteria")
    technologies: List[str] = Field(..., description="Relevant technologies, tools, or capabilities mentioned")
    evidences: List[str] = Field(..., description="Relevant text snippets supporting the findings upto a max of 5")
    confidence_level: str = Field(..., description="High/Medium/Low confidence in the assessment")

# Global LLM with Serper tools for direct extraction
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Create Serper search wrapper and tool
search = GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY)
serper_tool = Tool(
    name="search",
    func=search.run,
    description="Search the web using Serper to find information about companies relevant to the research goal."
)

llm_with_tools = llm.bind_tools([serper_tool])
llm_with_output = llm.with_structured_output(EvaluationOutput)

async def evaluate_company_with_serper_tool(company_name: str, domain: str, research_goal: str, quality_metrics: dict = None, search_depth: str = "standard") -> CompanyFinding:
    """Evaluate a company directly using LLM with Serper tools"""
    try:
        # Configure search depth based on search_depth parameter
        search_depth_configs = {
            "quick": {"num_results": 10, "description": "Quick search with 10 results"},
            "standard": {"num_results": 20, "description": "Standard search with 20 results"},
            "comprehensive": {"num_results": 30, "description": "Comprehensive search with 30 results"}
        }
        
        config = search_depth_configs.get(search_depth, search_depth_configs["standard"])
        search.k = config["num_results"]
        # print(f"🔍 Using {search_depth} search depth: {config['description']}")
        
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

IMPORTANT: Use this feedback to focus your search on addressing the specific gaps and issues for this company.
"""
                    break
        
        # Create comprehensive search message using research goal and quality feedback
        message = f"""
        Please search for and evaluate information about {company_name} ({domain}) regarding this goal: {research_goal}
        
        {company_feedback}
        
        Use the search tool to find comprehensive information about this company's:
        - Technologies, tools, and capabilities
        - Products and services
        - Case studies and examples
        - Partnerships and integrations
        - Market positioning and competitive advantages
        - Any evidence related to the goal
        
        After gathering information, evaluate whether this company meets the goal criteria.
        Return a structured assessment with:
        - goal_achieved: whether the company meets the  goal criteria
        - technologies: relevant technologies, tools, capabilities mentioned
        - evidences: key supporting evidence (up to 5 most relevant snippets) for the goal
        - confidence_level: High/Medium/Low confidence in the assessment
        """
        
        # Let the LLM use the search tool and evaluate directly
        response = await llm_with_output.ainvoke(message)
        
        # Convert confidence level to numeric score
        confidence_score = {
            "High": 0.9,
            "Medium": 0.6,
            "Low": 0.3
        }.get(response.confidence_level, 0.5)
        
        finding = CompanyFinding(
            domain=domain,
            confidence_score=confidence_score,
            evidence_sources=len(response.evidences),
            findings={
                "goal_achieved": response.goal_achieved,
                "technologies": response.technologies,
                "evidences": response.evidences,
                "confidence_level": response.confidence_level,
                "research_goal": research_goal
            },
            signals_found=len(response.evidences)
        )
        
        # print(f"🔍 Evaluated {company_name} ({domain}): {response.confidence_level} confidence, {len(response.evidences)} evidences")
        return finding
        
    except Exception as e:
        print(f"❌ Failed to evaluate {company_name} ({domain}): {e}")
        return None

def multi_source_search_agent(state: GTMState) -> GTMState:
    if not state.extracted_companies:
        raise ValueError("No extracted companies to search")

    if not SERPER_API_KEY:
        raise ValueError("SERPER_API_KEY not found in environment variables")

    search_goal = state.research_goal
    
    # Check if we have quality metrics for feedback
    quality_metrics = state.quality_metrics or {}
    if quality_metrics and 'company_analyses' in quality_metrics:
        print(f"🎯 Using quality metrics feedback for targeted searches")
        print(f"📊 Found quality data for {len(quality_metrics['company_analyses'])} companies")
    else:
        print(f"📝 Using default search strategies")

    print(f"🎯 Search depth: {state.search_depth}")

    # TIME QUERY GENERATION AND EVALUATION
    import time
    total_start = time.time()

    async def evaluate_companies():
        """Evaluate companies using research goal directly"""
        print(f"🔍 Evaluating {len(state.extracted_companies)} companies using goal...")
        
        # Create semaphore for concurrent processing
        sem = asyncio.Semaphore(state.max_parallel_searches)
        
        async def process_single_company(company):
            """Evaluate a single company using research goal directly"""
            async with sem:
                try:
                    # Evaluate company directly using Serper tools
                    finding = await evaluate_company_with_serper_tool(
                        company.name,
                        company.domain,
                        search_goal,
                        state.quality_metrics,
                        state.search_depth
                    )
                    
                    return finding
                    
                except Exception as e:
                    print(f"❌ Failed to process {company.name}: {e}")
                    return None
        
        # Run all evaluations in parallel
        evaluation_tasks = [process_single_company(company) for company in state.extracted_companies]
        all_findings = await asyncio.gather(*evaluation_tasks)
        
        # Filter out None results
        valid_findings = [finding for finding in all_findings if finding is not None]
        
        return valid_findings

    # Run the evaluation process
    findings = asyncio.run(evaluate_companies())
    
    total_end = time.time()
    total_duration = (total_end - total_start) * 1000
    print(f"⏱️  Total evaluation time: {total_duration:.2f}ms ({total_duration/1000:.2f}s)")

    print(f"\n📊 Evaluated {len(findings)} companies in {total_duration:.2f}ms.")

    # Save findings to disk for analysis
    os.makedirs("debug_output", exist_ok=True)
    output_path = os.path.join("debug_output", "final_findings.json")
    try:
        # Convert findings to serializable format
        findings_data = []
        for finding in findings:
            finding_dict = {
                "domain": finding.domain,
                "confidence_score": finding.confidence_score,
                "evidence_sources": finding.evidence_sources,
                "findings": finding.findings,
                "signals_found": finding.signals_found
            }
            findings_data.append(finding_dict)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(findings_data, f, ensure_ascii=False, indent=2)
        print(f"📁 Saved final findings to {output_path}")
    except Exception as e:
        print(f"⚠️ Failed to write final findings: {e}")

    # Increment iteration count for feedback loop tracking
    new_iteration_count = state.iteration_count + 1
    print(f"📊 Research Iteration: {new_iteration_count}/{state.max_iterations}")

    return state.model_copy(update={
        "final_findings": findings,
        "iteration_count": new_iteration_count
    })
