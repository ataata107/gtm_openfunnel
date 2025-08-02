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
1. Use different keywords and phrases
2. Target different information sources (news, company websites, technical blogs, etc.)
3. Focus on different aspects (technology, business, implementation, etc.)
4. Use various search techniques (quotes, site-specific, date ranges, etc.)
5. Target different stakeholders (developers, executives, analysts, etc.)

Examples of strategy types:
- Technology-focused: "machine learning fraud detection fintech"
- Company-focused: "stripe square fraud detection AI"
- Implementation-focused: "fraud detection API implementation"
- News-focused: "fintech AI fraud detection 2024"
- Technical-focused: "fraud detection algorithms fintech"
- Business-focused: "AI fraud prevention fintech companies"
- Product-focused: "fraud detection software fintech"
- Industry-focused: "payments fraud detection AI"
- Case study-focused: "fraud detection success stories fintech"
- Competitive-focused: "fraud detection market leaders fintech"

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
