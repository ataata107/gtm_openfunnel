from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from graph.state import GTMState
from typing import List
from dotenv import load_dotenv
import os
import time
import json

load_dotenv()



class QueryStrategyOutput(BaseModel):
    search_strategies_generated: List[str] = Field(..., description="List of search strategies for research")

# Global LLM instance for reuse - initialized once
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
structured_llm = llm.with_structured_output(QueryStrategyOutput)


def query_agent(state: GTMState) -> GTMState:
    total_start_time = time.time()
    print("🔍 QUERY AGENT: Starting search strategy generation...")
    print(f"📋 Research Goal: {state.research_goal}")
    print(f"🎯 Search Depth: {state.search_depth}")
    
    # Check if we have quality metrics from previous iteration
    quality_metrics = state.quality_metrics or {}
    has_quality_feedback = bool(quality_metrics)
    
    if has_quality_feedback:
        print("🎯 QUERY AGENT: Using quality metrics to improve search strategies")
        print(f"📊 Previous Quality Score: {quality_metrics.get('quality_score', 0):.2f}")
        print(f"📊 Previous Coverage Score: {quality_metrics.get('coverage_score', 0):.2f}")
    
    # Configure search depth - optimized for faster execution
    SEARCH_DEPTH_CONFIGS = {
        "quick": {"strategies": 10, "description": "10 focused search strategies"},
        "standard": {"strategies": 20, "description": "20 diverse search strategies"},
        "comprehensive": {"strategies": 30, "description": "30 comprehensive search strategies"}
    }
    
    config = SEARCH_DEPTH_CONFIGS.get(state.search_depth, SEARCH_DEPTH_CONFIGS["standard"])
    num_strategies = config["strategies"]
    
    print(f"🎯 QUERY AGENT: Generating {config['description']}")
    
    # Time quality feedback preparation
    feedback_start_time = time.time()
    
    # Prepare quality feedback text if available
    quality_feedback_text = ""
    if has_quality_feedback:
        missing_aspects = quality_metrics.get('missing_aspects', [])
        coverage_gaps = quality_metrics.get('coverage_gaps', [])
        evidence_issues = quality_metrics.get('evidence_issues', [])
        recommendations = quality_metrics.get('recommendations', [])
        
        # Convert lists to readable format
        missing_aspects_text = "\n".join([f"- {aspect}" for aspect in missing_aspects]) if missing_aspects else "None identified"
        coverage_gaps_text = "\n".join([f"- {gap}" for gap in coverage_gaps]) if coverage_gaps else "None identified"
        evidence_issues_text = "\n".join([f"- {issue}" for issue in evidence_issues]) if evidence_issues else "None identified"
        recommendations_text = "\n".join([f"- {rec}" for rec in recommendations]) if recommendations else "None provided"
        
        quality_feedback_text = f"""

PREVIOUS RESEARCH QUALITY ANALYSIS:
Quality Score: {quality_metrics.get('quality_score', 0):.2f}/1.0
Coverage Score: {quality_metrics.get('coverage_score', 0):.2f}/1.0

MISSING ASPECTS FROM PREVIOUS RESEARCH:
{missing_aspects_text}

COVERAGE GAPS FROM PREVIOUS RESEARCH:
{coverage_gaps_text}

EVIDENCE ISSUES FROM PREVIOUS RESEARCH:
{evidence_issues_text}

RECOMMENDATIONS FROM THIS RESEARCH:
{recommendations_text}

IMPORTANT: Use this quality feedback to generate more targeted search strategies that address the specific gaps and issues identified above.
"""
    
    feedback_prep_time = (time.time() - feedback_start_time) * 1000
    print(f"⏱️  Quality feedback preparation took: {feedback_prep_time:.2f}ms")

    prompt = PromptTemplate.from_template(
        """Generate {num_strategies} diverse search strategies for: {research_goal}{quality_feedback}

{quality_guidance}

Strategy types to adapt to make the search strategies more diverse:
- Technology: specific tools, implementations
- Company: competitors, market leaders  
- News: recent announcements, developments
- Technical: documentation, methodologies
- Business: market analysis, trends
- Product: features, capabilities
- Case studies: success stories, examples

IMPORTANT: Return ONLY clean, direct search terms without any prefixes, instructions, or unnecessary words.
Examples of diverse search strategies:
- "AI fraud detection companies"
- "machine learning fraud prevention tools"
- "Companies using AWS"
- "Companies who are in te process of getting SOC 2"
Avoid phrases like "Search for...", "Find...", "Look for...", "Companies that...", etc.
Return exactly {num_strategies} clean, direct and distinct search terms as 'search_strategies_generated'.
"""
    )

    # Prepare quality guidance based on whether we have feedback
    if has_quality_feedback:
        quality_guidance = """
Quality-driven guidelines:
- Address missing aspects and coverage gaps
- Use reliable data sources
- Follow previous recommendations
- Low quality score: more specific searches
- Low coverage score: broader searches
- Evidence issues: recent, specific information
"""
    else:
        quality_guidance = ""

    # Time prompt formatting
    prompt_start_time = time.time()
    input_text = prompt.format(
        research_goal=state.research_goal,
        quality_feedback=quality_feedback_text,
        quality_guidance=quality_guidance,
        num_strategies=num_strategies
    )
    prompt_format_time = (time.time() - prompt_start_time) * 1000
    print(f"⏱️  Prompt formatting took: {prompt_format_time:.2f}ms")
    
    # Time LLM invocation
    llm_invoke_start_time = time.time()
    print("🤖 QUERY AGENT: Invoking LLM for strategy generation...")
    response: QueryStrategyOutput = structured_llm.invoke(input_text)
    llm_invoke_time = (time.time() - llm_invoke_start_time) * 1000
    print(f"⏱️  LLM invocation took: {llm_invoke_time:.2f}ms")

    # Calculate total time
    total_time = (time.time() - total_start_time) * 1000
    print(f"⏱️  Total query agent time: {total_time:.2f}ms ({total_time/1000:.2f}s)")
    
    print(f"✅ QUERY AGENT: Generated {len(response.search_strategies_generated)} search strategies")
    if has_quality_feedback:
        print("🎯 QUERY AGENT: Strategies generated with quality feedback integration")
    
    # Save search strategies to debug file
    try:
        os.makedirs("debug_output", exist_ok=True)
        output_path = os.path.join("debug_output", "search_strategies.json")
        
        strategies_data = {
            "research_goal": state.research_goal,
            "search_depth": state.search_depth,
            "num_strategies": len(response.search_strategies_generated),
            "strategies": response.search_strategies_generated,
            "quality_feedback_used": has_quality_feedback,
            "timestamp": time.time()
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(strategies_data, f, ensure_ascii=False, indent=2)
        print(f"📁 Saved search strategies to {output_path}")
        
    except Exception as e:
        print(f"⚠️ Failed to write search strategies: {e}")
    
    return state.model_copy(update={"search_strategies_generated": response.search_strategies_generated})
