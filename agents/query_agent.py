from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from graph.state import GTMState
from typing import List
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class QueryStrategyOutput(BaseModel):
    search_strategies_generated: List[str] = Field(..., description="List of search strategies for research")


def query_agent(state: GTMState) -> GTMState:
    logger.info("🔍 QUERY AGENT: Starting search strategy generation...")
    logger.info(f"📋 Research Goal: {state.research_goal}")
    logger.info(f"🎯 Search Depth: {state.search_depth}")
    
    # Check if we have quality metrics from previous iteration
    quality_metrics = state.quality_metrics or {}
    has_quality_feedback = bool(quality_metrics)
    
    if has_quality_feedback:
        logger.info("🎯 QUERY AGENT: Using quality metrics to improve search strategies")
        logger.info(f"📊 Previous Quality Score: {quality_metrics.get('quality_score', 0):.2f}")
        logger.info(f"📊 Previous Coverage Score: {quality_metrics.get('coverage_score', 0):.2f}")
    
    # Configure search depth
    SEARCH_DEPTH_CONFIGS = {
        "quick": {"strategies": 8, "description": "8 focused search strategies"},
        "standard": {"strategies": 15, "description": "15 diverse search strategies"},
        "comprehensive": {"strategies": 25, "description": "25 comprehensive search strategies"}
    }
    
    config = SEARCH_DEPTH_CONFIGS.get(state.search_depth, SEARCH_DEPTH_CONFIGS["standard"])
    num_strategies = config["strategies"]
    
    logger.info(f"🎯 QUERY AGENT: Generating {config['description']}")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    structured_llm = llm.with_structured_output(QueryStrategyOutput)

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

    prompt = PromptTemplate.from_template(
        """You are a research strategist specializing in web search optimization.

Your task is to generate {num_strategies} different search strategies for the following research goal. Each strategy should restructure the research goal in a unique way to find different types of information.

Research goal: {research_goal}{quality_feedback}

Generate {num_strategies} diverse search strategies that:
1. Use different keywords and phrases related to the research goal
2. Target different information sources (news, company websites, technical blogs, job boards, etc.)
3. Focus on different aspects (technology, business, implementation, market, etc.)
4. Use various search techniques (quotes, site-specific, date ranges, etc.)
5. Target different stakeholders (developers, executives, analysts, customers, etc.)

Strategy generation guidelines:
- Break down the research goal into different components and keywords
- Create variations that focus on different aspects of the goal
- Include industry-specific terms and jargon
- Use different search operators and techniques
- Target both broad and specific search terms
- Consider different time periods and contexts
- Include both technical and business perspectives

{quality_guidance}

Examples of strategy types (adapt these to your specific research goal):
- Technology-focused: Focus on specific technologies, tools, or technical implementations
- Company-focused: Target specific companies or competitors
- Implementation-focused: Look for implementation details, APIs, or technical guides
- News-focused: Search for recent news, announcements, or developments
- Technical-focused: Focus on technical documentation, algorithms, or methodologies
- Business-focused: Look for business cases, market analysis, or industry trends
- Product-focused: Search for product features, capabilities, or solutions
- Industry-focused: Target industry-specific terms and contexts
- Case study-focused: Look for success stories, case studies, or examples
- Competitive-focused: Search for market leaders, competitors, or industry analysis

Return exactly {num_strategies} search strategies as the 'search_strategies_generated' field of a Pydantic model. 
"""
    )

    # Prepare quality guidance based on whether we have feedback
    if has_quality_feedback:
        quality_guidance = """
IMPORTANT QUALITY-DRIVEN GUIDELINES:
- Focus on strategies that address the specific missing aspects identified
- Prioritize searches that target the coverage gaps mentioned
- Generate strategies that use more reliable data sources (address evidence issues)
- Include strategies that follow the recommendations from previous research
- If quality score was low, focus on more specific and targeted searches
- If coverage score was low, focus on broader and more diverse searches
- If evidence issues were identified, prioritize searches for recent, specific, and well-documented information
"""
    else:
        quality_guidance = ""

    input_text = prompt.format(
        research_goal=state.research_goal,
        quality_feedback=quality_feedback_text,
        quality_guidance=quality_guidance,
        num_strategies=num_strategies
    )
    
    logger.info("🤖 QUERY AGENT: Invoking LLM for strategy generation...")
    response: QueryStrategyOutput = structured_llm.invoke(input_text)

    logger.info(f"✅ QUERY AGENT: Generated {len(response.search_strategies_generated)} search strategies")
    if has_quality_feedback:
        logger.info("🎯 QUERY AGENT: Strategies generated with quality feedback integration")
    
    return state.model_copy(update={"search_strategies_generated": response.search_strategies_generated})
