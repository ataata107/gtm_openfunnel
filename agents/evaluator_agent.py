# agents/evaluator_agent.py

from graph.state import GTMState, CompanyFinding
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List, Dict
import time
import asyncio
import os
import json

# Dynamic output structure based on research goal
class EvaluationOutput(BaseModel):
    goal_achieved: bool = Field(..., description="Whether the company meets the research goal criteria")
    technologies: List[str] = Field(..., description="Relevant technologies, tools, or capabilities mentioned")
    evidences: List[str] = Field(..., description="Relevant text snippets supporting the findings")
    confidence_level: str = Field(..., description="High/Medium/Low confidence in the assessment")

class LLMEvidenceEvaluator:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.structured_llm = self.llm.with_structured_output(EvaluationOutput)
        self.prompt = PromptTemplate.from_template(
            """You are a research analyst. Given raw evidences about a company and a research goal, extract structured findings.

Research goal: {research_goal}
Company: {company}
Raw evidences:
{evidence}

Analyze the evidences to determine if the company meets the research goal criteria. Look for:
1. Direct mentions or evidence related to the research goal by the company itself
2. Technologies, tools, or capabilities that align with the goal
3. Case studies, examples, or descriptions that demonstrate relevance
4. Any quantitative data or metrics related to the goal

Return a Pydantic model with:
- goal_achieved: whether the company meets the research goal criteria
- technologies: relevant technologies, tools, or capabilities mentioned
- evidences: list of relevant snippets from the input
- confidence_level: High/Medium/Low confidence in the assessment
"""
        )

    async def evaluate_async(self, research_goal: str, company: str, evidence: List[str]) -> EvaluationOutput:
        """Async version of evaluate using ainvoke"""
        input_text = self.prompt.format(
            research_goal=research_goal,
            company=company,
            evidence="\n".join(evidence)
        )
        return await self.structured_llm.ainvoke(input_text)


def evaluator_agent(state: GTMState) -> GTMState:
    if not state.search_results_serper and not state.search_results_website:
        raise ValueError("No evidence to evaluate")

    evaluator = LLMEvidenceEvaluator()
    findings = []
    total_snippets = 0
    
    # TIME EVALUATION
    import time
    eval_start = time.time()

    # Run evaluations asynchronously
    async def evaluate_companies_async():
        nonlocal total_snippets  # Use nonlocal instead of global
        sem = asyncio.Semaphore(state.max_parallel_searches)  # Limit concurrent LLM calls
        
        async def evaluate_single_company(company):
            async with sem:
                domain = company.domain

                # 🔁 Merge evidence from both search sources
                evidence_snippets = []
                serper_snippets = []
                website_snippets = []
                
                if state.search_results_serper and domain in state.search_results_serper:
                    serper_snippets = state.search_results_serper[domain]
                    evidence_snippets.extend(serper_snippets)
                if state.search_results_website and domain in state.search_results_website:
                    website_snippets = state.search_results_website[domain]
                    evidence_snippets.extend(website_snippets)

                if not evidence_snippets:
                    return None

                # print(f"Total Evidence snippets: {len(evidence_snippets)} for company: {company.name} | Serper snippets: {len(serper_snippets)} | Website snippets: {len(website_snippets)}")

                try:
                    # Use async evaluation
                    structured = await evaluator.evaluate_async(state.research_goal, company.name, evidence_snippets)
                    
                    # Convert confidence level to numeric score
                    confidence_score = {
                        "High": 0.9,
                        "Medium": 0.6,
                        "Low": 0.3
                    }.get(structured.confidence_level, 0.5)
                    
                    finding = CompanyFinding(
                        domain=domain,
                        confidence_score=confidence_score,
                        evidence_sources=len(evidence_snippets),
                        findings={
                            "goal_achieved": structured.goal_achieved,
                            "technologies": structured.technologies,
                            "evidences": structured.evidences,
                            "confidence_level": structured.confidence_level,
                            "research_goal": state.research_goal
                        },
                        signals_found=len(structured.evidences)
                    )
                    return finding
                except Exception as e:
                    print(f"❌ Failed to evaluate {domain}:", e)
                    return None

        # Run all evaluations in parallel
        evaluation_tasks = [evaluate_single_company(company) for company in state.extracted_companies or []]
        all_findings = await asyncio.gather(*evaluation_tasks)
        
        # Process results and collect valid findings
        for finding in all_findings:
            if finding is not None:
                findings.append(finding)
                total_snippets += finding.evidence_sources

    # Run the async evaluation
    asyncio.run(evaluate_companies_async())

    eval_end = time.time()
    eval_duration = (eval_end - eval_start) * 1000
    print(f"⏱️  Evaluation took: {eval_duration:.2f}ms ({eval_duration/1000:.2f}s)")

    print(f"\n📊 Evaluated {len(findings)} companies from {total_snippets} snippets in {eval_duration:.2f}ms.")

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

    return state.model_copy(update={"final_findings": findings})
