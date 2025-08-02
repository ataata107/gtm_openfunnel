# agents/quality_evaluator_agent.py

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

# Individual company quality analysis
class CompanyQualityAnalysis(BaseModel):
    company_domain: str = Field(..., description="Company domain")
    quality_score: float = Field(..., description="Quality score for this company (0-1)")
    coverage_score: float = Field(..., description="Coverage score for this company (0-1)")
    gaps: List[str] = Field(..., description="Specific gaps for this company")
    evidence_issues: List[str] = Field(..., description="Evidence quality issues for this company")
    recommendations: List[str] = Field(..., description="Company-specific recommendations")

# Overall aggregated analysis
class CoverageAnalysis(BaseModel):
    coverage_score: float = Field(..., description="Overall coverage score (0-1)")
    missing_aspects: List[str] = Field(..., description="List of missing research aspects")
    coverage_gaps: List[str] = Field(..., description="Specific gaps in research coverage")
    quality_score: float = Field(..., description="Overall evidence quality score (0-1)")
    evidence_issues: List[str] = Field(..., description="Issues with evidence quality")
    recommendations: List[str] = Field(..., description="Recommendations for improvement")
    company_analyses: List[CompanyQualityAnalysis] = Field(..., description="Individual company analyses")

class CompanyQualityEvaluator:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.structured_llm = self.llm.with_structured_output(CompanyQualityAnalysis)
        
        self.company_prompt = PromptTemplate.from_template(
            """You are a research quality analyst. Analyze the quality and coverage for a single company's findings.

Research Goal: {research_goal}

Company Analysis:
Company: {company_domain}
Confidence Score: {confidence_score}
Evidence Sources: {evidence_sources}
Goal Achieved: {goal_achieved}
Technologies: {technologies}
Evidence Snippets: {evidence_snippets}

Analyze this company's research quality and coverage:

1. **Quality Analysis:**
   - How reliable is the evidence for this company?
   - Are there issues with the evidence quality?
   - Is the evidence recent and relevant?

2. **Coverage Analysis:**
   - How well does this company's data cover the research goal?
   - What specific information is missing for this company?
   - Are there gaps in the analysis?

3. **Gap Identification:**
   - What specific information is missing for this company?
   - What additional research would help for this company?

Return a structured analysis with:
- company_domain: The company domain
- quality_score: 0-1 score of evidence quality for this company
- coverage_score: 0-1 score of how well this company covers the goal
- gaps: List of specific gaps for this company
- evidence_issues: Problems with evidence for this company
- recommendations: Company-specific recommendations
"""
        )

    async def evaluate_single_company(self, finding, research_goal):
        """Evaluate quality and coverage for a single company"""
        
        # Prepare evidence snippets (limit to avoid token issues)
        evidence_snippets = finding.findings.get('evidences', [])
        if len(evidence_snippets) > 5:
            evidence_snippets = evidence_snippets[:5]  # Show first 5 snippets
        
        input_text = self.company_prompt.format(
            research_goal=research_goal,
            company_domain=finding.domain,
            confidence_score=finding.confidence_score,
            evidence_sources=finding.evidence_sources,
            goal_achieved=finding.findings.get('goal_achieved', 'N/A'),
            technologies=finding.findings.get('technologies', []),
            evidence_snippets=evidence_snippets
        )
        
        return await self.structured_llm.ainvoke(input_text)

class QualityEvaluator:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.structured_llm = self.llm.with_structured_output(CoverageAnalysis)
        self.company_evaluator = CompanyQualityEvaluator()
        
        self.aggregation_prompt = PromptTemplate.from_template(
            """You are a research quality analyst. Aggregate individual company analyses into an overall assessment.

Research Goal: {research_goal}

Individual Company Analyses:
{company_analyses}

Overall Statistics:
- Total companies analyzed: {total_companies}
- Average quality score: {avg_quality_score}
- Average coverage score: {avg_coverage_score}
- Companies with high quality (≥0.8): {high_quality_count}
- Companies with low quality (<0.5): {low_quality_count}

Analyze the overall research coverage and quality:

1. **Overall Coverage Analysis:**
   - How well does the research cover the stated goal across all companies?
   - What aspects of the research goal are missing?
   - Are there gaps in company types, technologies, or use cases?

2. **Overall Quality Analysis:**
   - How reliable is the evidence across all companies?
   - Are there common issues with evidence quality?
   - Is the evidence recent and relevant?

3. **Gap Identification:**
   - What specific information is missing across companies?
   - Which companies or technologies need deeper research?
   - What additional search strategies would help?

Return a structured analysis with:
- coverage_score: 0-1 score of how well the goal is covered
- missing_aspects: List of missing research aspects
- coverage_gaps: Specific gaps that need addressing
- quality_score: 0-1 score of evidence quality
- evidence_issues: Problems with current evidence
- recommendations: Specific actions to improve research
- company_analyses: List of individual company analyses
"""
        )

    async def analyze_coverage_and_quality_parallel(self, state: GTMState) -> CoverageAnalysis:
        """Analyze quality and coverage using parallel company evaluations"""
        
        print(f"🔍 Running parallel quality analysis for {len(state.final_findings)} companies...")
        
        # Run parallel evaluations for each company
        company_tasks = [
            self.company_evaluator.evaluate_single_company(finding, state.research_goal)
            for finding in state.final_findings
        ]
        
        company_analyses = await asyncio.gather(*company_tasks)
        
        # Calculate aggregate statistics
        avg_quality_score = sum(analysis.quality_score for analysis in company_analyses) / len(company_analyses)
        avg_coverage_score = sum(analysis.coverage_score for analysis in company_analyses) / len(company_analyses)
        high_quality_count = len([a for a in company_analyses if a.quality_score >= 0.8])
        low_quality_count = len([a for a in company_analyses if a.quality_score < 0.5])
        
        # Prepare company analyses text for aggregation
        company_analyses_text = ""
        for analysis in company_analyses:
            company_analyses_text += f"""
            Company: {analysis.company_domain}
            Quality Score: {analysis.quality_score:.2f}
            Coverage Score: {analysis.coverage_score:.2f}
            Gaps: {analysis.gaps}
            Issues: {analysis.evidence_issues}
            Recommendations: {analysis.recommendations}
            """
        
        # Generate overall analysis
        input_text = self.aggregation_prompt.format(
            research_goal=state.research_goal,
            company_analyses=company_analyses_text,
            total_companies=len(company_analyses),
            avg_quality_score=round(avg_quality_score, 2),
            avg_coverage_score=round(avg_coverage_score, 2),
            high_quality_count=high_quality_count,
            low_quality_count=low_quality_count
        )
        
        overall_analysis = self.structured_llm.invoke(input_text)
        
        # Add company analyses to the result
        overall_analysis.company_analyses = company_analyses
        
        return overall_analysis

def quality_evaluator_agent(state: GTMState) -> GTMState:
    """Analyze research coverage and quality using parallel company evaluations"""
    
    if not state.final_findings:
        print("⚠️ No findings to evaluate. Skipping quality evaluation.")
        return state
    
    print("🔍 Analyzing research coverage and quality (parallel processing)...")
    
    evaluator = QualityEvaluator()
    
    try:
        # Run parallel analysis
        analysis = asyncio.run(evaluator.analyze_coverage_and_quality_parallel(state))
        
        # print(f"📊 Quality Analysis Results:")
        # print(f"  Coverage Score: {analysis.coverage_score:.2f}/1.0")
        # print(f"  Quality Score: {analysis.quality_score:.2f}/1.0")
        # print(f"  Missing Aspects: {len(analysis.missing_aspects)}")
        # print(f"  Coverage Gaps: {len(analysis.coverage_gaps)}")
        # print(f"  Evidence Issues: {len(analysis.evidence_issues)}")
        # print(f"  Companies Analyzed: {len(analysis.company_analyses)}")
        
        # Show individual company results
        # print(f"\n📋 Individual Company Results:")
        # for company_analysis in analysis.company_analyses:
        #     print(f"  {company_analysis.company_domain}:")
        #     print(f"    Quality: {company_analysis.quality_score:.2f}, Coverage: {company_analysis.coverage_score:.2f}")
        #     if company_analysis.gaps:
        #         print(f"    Gaps: {len(company_analysis.gaps)}")
        
        # if analysis.missing_aspects:
        #     print(f"  🚨 Missing Aspects:")
        #     for aspect in analysis.missing_aspects:
        #         print(f"    - {aspect}")
        
        # if analysis.coverage_gaps:
        #     print(f"  📋 Coverage Gaps:")
        #     for gap in analysis.coverage_gaps:
        #         print(f"    - {gap}")
        
        # if analysis.recommendations:
        #     print(f"  💡 Recommendations:")
        #     for rec in analysis.recommendations:
        #         print(f"    - {rec}")
        
        # Save analysis to debug output
        os.makedirs("debug_output", exist_ok=True)
        output_path = os.path.join("debug_output", "quality_analysis.json")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(analysis.dict(), f, ensure_ascii=False, indent=2)
            print(f"📁 Saved quality analysis to {output_path}")
        except Exception as e:
            print(f"⚠️ Failed to write quality analysis: {e}")
        
        # Update state with quality metrics
        quality_metrics = {
            "coverage_score": analysis.coverage_score,
            "quality_score": analysis.quality_score,
            "missing_aspects": analysis.missing_aspects,
            "coverage_gaps": analysis.coverage_gaps,
            "evidence_issues": analysis.evidence_issues,
            "recommendations": analysis.recommendations,
            "company_analyses": [analysis.dict() for analysis in analysis.company_analyses]
        }
        
        return state.model_copy(update={"quality_metrics": quality_metrics})
        
    except Exception as e:
        print(f"❌ Quality evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return state 