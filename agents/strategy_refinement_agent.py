# agents/strategy_refinement_agent.py

from graph.state import GTMState
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import asyncio
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Strategy refinement output structure
class RefinedStrategy(BaseModel):
    strategy_type: str = Field(..., description="Type of strategy (gap_filling, quality_improvement, coverage_expansion)")
    search_queries: List[str] = Field(..., description="List of refined search queries")
    target_companies: List[str] = Field(..., description="Specific companies to target")
    data_sources: List[str] = Field(..., description="Recommended data sources")
    reasoning: str = Field(..., description="Explanation of why this strategy was chosen")
    priority: int = Field(..., description="Priority level (1-5, 5 being highest)")

class StrategyRefinementOutput(BaseModel):
    refined_strategies: List[RefinedStrategy] = Field(..., description="List of refined search strategies")
    total_new_queries: int = Field(..., description="Total number of new queries generated")
    implementation_notes: List[str] = Field(..., description="Notes for implementing the strategies")

class StrategyRefiner:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)  # Slight creativity for strategy generation
        self.structured_llm = self.llm.with_structured_output(StrategyRefinementOutput)
        
        self.prompt = PromptTemplate.from_template(
            """You are a research strategy expert. Analyze the current research gaps and quality issues to generate improved search strategies.

Research Goal: {research_goal}

Current Research Status:
- Original search strategies: {original_strategies_count}
- Companies analyzed: {companies_analyzed}
- Average quality score: {avg_quality_score}
- Average coverage score: {avg_coverage_score}

Quality Analysis Results:
- Missing Aspects: {missing_aspects}
- Coverage Gaps: {coverage_gaps}
- Evidence Issues: {evidence_issues}
- Recommendations: {recommendations}

Individual Company Analysis:
{company_analyses}

Current Search Strategies:
{current_strategies}

Based on the gaps and quality issues identified, generate refined search strategies that will:

1. **Address Coverage Gaps:**
   - Generate queries for missing company types
   - Target specific technologies or use cases
   - Focus on underrepresented sectors

2. **Improve Quality:**
   - Target more reliable data sources
   - Generate queries for specific evidence types
   - Focus on recent and relevant information

3. **Expand Scope:**
   - Generate queries for related technologies
   - Target complementary use cases
   - Include broader industry context

Generate 3-5 refined strategies, each with:
- strategy_type: The type of strategy (gap_filling, quality_improvement, coverage_expansion)
- search_queries: 3-5 specific search queries for this strategy
- target_companies: Specific companies to focus on (if applicable)
- data_sources: Recommended data sources for this strategy
- reasoning: Why this strategy addresses the identified gaps
- priority: Priority level (1-5, 5 being highest)

Focus on actionable, specific strategies that directly address the identified gaps.
"""
        )

    def generate_refined_strategies(self, state: GTMState) -> StrategyRefinementOutput:
        """Generate refined search strategies based on quality analysis"""
        
        # Extract quality metrics
        quality_metrics = state.quality_metrics or {}
        missing_aspects = quality_metrics.get('missing_aspects', [])
        coverage_gaps = quality_metrics.get('coverage_gaps', [])
        evidence_issues = quality_metrics.get('evidence_issues', [])
        recommendations = quality_metrics.get('recommendations', [])
        company_analyses = quality_metrics.get('company_analyses', [])
        
        # Prepare company analysis text
        company_analyses_text = ""
        if company_analyses:
            for analysis in company_analyses[:5]:  # Show first 5 for brevity
                company_analyses_text += f"""
                Company: {analysis.get('company_domain', 'N/A')}
                Quality: {analysis.get('quality_score', 0):.2f}
                Coverage: {analysis.get('coverage_score', 0):.2f}
                Gaps: {analysis.get('gaps', [])}
                """
        
        # Prepare current strategies text
        current_strategies = state.search_strategies_generated or []
        current_strategies_text = "\n".join([f"- {strategy}" for strategy in current_strategies[:10]])
        
        # Calculate metrics
        companies_analyzed = len(state.final_findings or [])
        avg_quality_score = quality_metrics.get('quality_score', 0)
        avg_coverage_score = quality_metrics.get('coverage_score', 0)
        
        input_text = self.prompt.format(
            research_goal=state.research_goal,
            original_strategies_count=len(current_strategies),
            companies_analyzed=companies_analyzed,
            avg_quality_score=round(avg_quality_score, 2),
            avg_coverage_score=round(avg_coverage_score, 2),
            missing_aspects=missing_aspects,
            coverage_gaps=coverage_gaps,
            evidence_issues=evidence_issues,
            recommendations=recommendations,
            company_analyses=company_analyses_text,
            current_strategies=current_strategies_text
        )
        
        return self.structured_llm.invoke(input_text)

def strategy_refinement_agent(state: GTMState) -> GTMState:
    """Generate refined search strategies based on quality analysis"""
    
    if not state.quality_metrics:
        print("⚠️ No quality metrics available. Skipping strategy refinement.")
        return state
    
    print("🎯 Generating refined search strategies based on quality analysis...")
    
    refiner = StrategyRefiner()
    
    try:
        refinement_output = refiner.generate_refined_strategies(state)
        
        print(f"📊 Strategy Refinement Results:")
        print(f"  Refined Strategies: {len(refinement_output.refined_strategies)}")
        print(f"  Total New Queries: {refinement_output.total_new_queries}")
        
        # Show refined strategies
        for i, strategy in enumerate(refinement_output.refined_strategies, 1):
            print(f"\n🎯 Strategy {i}: {strategy.strategy_type.upper()}")
            print(f"  Priority: {strategy.priority}/5")
            print(f"  Target Companies: {strategy.target_companies}")
            print(f"  Data Sources: {strategy.data_sources}")
            print(f"  Reasoning: {strategy.reasoning}")
            print(f"  Queries ({len(strategy.search_queries)}):")
            for j, query in enumerate(strategy.search_queries, 1):
                print(f"    {j}. {query}")
        
        # Save refinement results
        os.makedirs("debug_output", exist_ok=True)
        output_path = os.path.join("debug_output", "strategy_refinement.json")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(refinement_output.dict(), f, ensure_ascii=False, indent=2)
            print(f"📁 Saved strategy refinement to {output_path}")
        except Exception as e:
            print(f"⚠️ Failed to write strategy refinement: {e}")
        
        # Update state with refined strategies
        # Extract all new queries from refined strategies
        all_new_queries = []
        for strategy in refinement_output.refined_strategies:
            all_new_queries.extend(strategy.search_queries)
        
        # Combine with existing strategies
        existing_strategies = state.search_strategies_generated or []
        combined_strategies = existing_strategies + all_new_queries
        
        # Store refinement results
        refinement_results = {
            "refined_strategies": [strategy.dict() for strategy in refinement_output.refined_strategies],
            "total_new_queries": refinement_output.total_new_queries,
            "implementation_notes": refinement_output.implementation_notes
        }
        
        return state.model_copy(update={
            "search_strategies_generated": combined_strategies,
            "strategy_refinement": refinement_results
        })
        
    except Exception as e:
        print(f"❌ Strategy refinement failed: {e}")
        import traceback
        traceback.print_exc()
        return state 