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
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    structured_llm = llm.with_structured_output(QueryStrategyOutput)

    prompt = PromptTemplate.from_template(
        """You are a research strategist specializing in web search optimization.

Your task is to generate 10 different search strategies for the following research goal. Each strategy should restructure the research goal in a unique way to find different types of information.

Research goal: {research_goal}

Generate 10 diverse search strategies that:
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

Return exactly 10 search strategies as the 'search_strategies_generated' field of a Pydantic model. 
"""
    )

    input_text = prompt.format(research_goal=state.research_goal)
    logger.info("🤖 QUERY AGENT: Invoking LLM for strategy generation...")
    response: QueryStrategyOutput = structured_llm.invoke(input_text)

    logger.info(f"✅ QUERY AGENT: Generated {len(response.search_strategies_generated)} search strategies")
    # for i, strategy in enumerate(response.search_strategies_generated, 1):
    #     logger.info(f"   {i}. {strategy}")

    return state.model_copy(update={"search_strategies_generated": response.search_strategies_generated})
