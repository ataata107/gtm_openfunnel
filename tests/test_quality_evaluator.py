#!/usr/bin/env python3
"""
Test for quality evaluator agent functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.quality_evaluator_agent import CompanyQualityEvaluator, QualityEvaluator, CompanyQualityAnalysis, CoverageAnalysis
from graph.state import GTMState, CompanyFinding
from typing import List, Dict, Any
import asyncio

def create_mock_finding(domain: str, confidence_score: float, evidence_sources: int, goal_achieved: bool, technologies: List[str], evidences: List[str]) -> CompanyFinding:
    """Create a mock company finding for testing"""
    return CompanyFinding(
        domain=domain,
        confidence_score=confidence_score,
        evidence_sources=evidence_sources,
        findings={
            "goal_achieved": goal_achieved,
            "technologies": technologies,
            "evidences": evidences,
            "confidence_level": "High" if confidence_score > 0.8 else "Medium" if confidence_score > 0.5 else "Low"
        },
        signals_found=len(evidences)
    )

def create_mock_state(research_goal: str, findings: List[CompanyFinding]) -> GTMState:
    """Create a mock state for testing"""
    return GTMState(
        research_goal=research_goal,
        search_depth="comprehensive",
        max_parallel_searches=5,
        confidence_threshold=0.8,
        final_findings=findings
    )

async def test_company_quality_evaluator():
    """Test individual company quality evaluation"""
    print("🧪 Testing Company Quality Evaluator")
    print("=" * 50)
    
    evaluator = CompanyQualityEvaluator()
    
    # Test case 1: High quality company
    high_quality_finding = create_mock_finding(
        domain="stripe.com",
        confidence_score=0.92,
        evidence_sources=15,
        goal_achieved=True,
        technologies=["TensorFlow", "scikit-learn", "machine learning"],
        evidences=[
            "Stripe uses advanced machine learning for fraud detection",
            "AI-powered risk assessment system processes millions of transactions",
            "Real-time fraud detection with 99.9% accuracy",
            "Machine learning models trained on billions of transactions"
        ]
    )
    
    print("\n📋 Test Case 1: High Quality Company (Stripe)")
    try:
        result = await evaluator.evaluate_single_company(high_quality_finding, "Find fintech companies using AI for fraud detection")
        print(f"✅ Quality Score: {result.quality_score:.2f}")
        print(f"✅ Coverage Score: {result.coverage_score:.2f}")
        print(f"✅ Gaps: {result.gaps}")
        print(f"✅ Issues: {result.evidence_issues}")
        print(f"✅ Recommendations: {result.recommendations}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test case 2: Medium quality company
    medium_quality_finding = create_mock_finding(
        domain="square.com",
        confidence_score=0.65,
        evidence_sources=8,
        goal_achieved=True,
        technologies=["AI", "data analytics"],
        evidences=[
            "Square uses AI for payment processing",
            "Advanced analytics for business insights"
        ]
    )
    
    print("\n📋 Test Case 2: Medium Quality Company (Square)")
    try:
        result = await evaluator.evaluate_single_company(medium_quality_finding, "Find fintech companies using AI for fraud detection")
        print(f"✅ Quality Score: {result.quality_score:.2f}")
        print(f"✅ Coverage Score: {result.coverage_score:.2f}")
        print(f"✅ Gaps: {result.gaps}")
        print(f"✅ Issues: {result.evidence_issues}")
        print(f"✅ Recommendations: {result.recommendations}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test case 3: Low quality company
    low_quality_finding = create_mock_finding(
        domain="unknown.com",
        confidence_score=0.35,
        evidence_sources=3,
        goal_achieved=False,
        technologies=["technology"],
        evidences=[
            "Company uses technology for payments"
        ]
    )
    
    print("\n📋 Test Case 3: Low Quality Company (Unknown)")
    try:
        result = await evaluator.evaluate_single_company(low_quality_finding, "Find fintech companies using AI for fraud detection")
        print(f"✅ Quality Score: {result.quality_score:.2f}")
        print(f"✅ Coverage Score: {result.coverage_score:.2f}")
        print(f"✅ Gaps: {result.gaps}")
        print(f"✅ Issues: {result.evidence_issues}")
        print(f"✅ Recommendations: {result.recommendations}")
    except Exception as e:
        print(f"❌ Failed: {e}")

async def test_quality_evaluator_aggregation():
    """Test overall quality evaluation and aggregation"""
    print("\n🧪 Testing Quality Evaluator Aggregation")
    print("=" * 50)
    
    evaluator = QualityEvaluator()
    
    # Create mock findings
    findings = [
        create_mock_finding(
            domain="stripe.com",
            confidence_score=0.92,
            evidence_sources=15,
            goal_achieved=True,
            technologies=["TensorFlow", "scikit-learn"],
            evidences=["Stripe uses machine learning for fraud detection", "AI-powered risk assessment"]
        ),
        create_mock_finding(
            domain="square.com",
            confidence_score=0.75,
            evidence_sources=10,
            goal_achieved=True,
            technologies=["AI", "analytics"],
            evidences=["Square uses AI for payment processing", "Advanced analytics platform"]
        ),
        create_mock_finding(
            domain="paypal.com",
            confidence_score=0.68,
            evidence_sources=8,
            goal_achieved=True,
            technologies=["machine learning"],
            evidences=["PayPal uses ML for fraud prevention"]
        ),
        create_mock_finding(
            domain="unknown.com",
            confidence_score=0.45,
            evidence_sources=3,
            goal_achieved=False,
            technologies=["technology"],
            evidences=["Company uses technology"]
        )
    ]
    
    # Create mock state
    state = create_mock_state("Find fintech companies using AI for fraud detection", findings)
    
    print(f"📊 Testing aggregation for {len(findings)} companies")
    print(f"🎯 Research Goal: {state.research_goal}")
    
    try:
        result = await evaluator.analyze_coverage_and_quality_parallel(state)
        
        print(f"\n✅ Overall Quality Score: {result.quality_score:.2f}")
        print(f"✅ Overall Coverage Score: {result.coverage_score:.2f}")
        print(f"✅ Missing Aspects: {result.missing_aspects}")
        print(f"✅ Coverage Gaps: {result.coverage_gaps}")
        print(f"✅ Evidence Issues: {result.evidence_issues}")
        print(f"✅ Recommendations: {result.recommendations}")
        print(f"✅ Company Analyses: {len(result.company_analyses)} companies analyzed")
        
    except Exception as e:
        print(f"❌ Aggregation failed: {e}")

async def test_different_research_goals():
    """Test quality evaluator with different research goals"""
    print("\n🧪 Testing Different Research Goals")
    print("=" * 50)
    
    research_goals = [
        "Find companies using Kubernetes in production",
        "Find B2B SaaS companies with 50-200 employees",
        "Find healthcare companies using AI for diagnosis",
        "Find companies using blockchain for supply chain",
        "Find companies with remote-first culture"
    ]
    
    # Create a standard finding for testing
    standard_finding = create_mock_finding(
        domain="test.com",
        confidence_score=0.75,
        evidence_sources=10,
        goal_achieved=True,
        technologies=["technology"],
        evidences=["Company uses technology for business"]
    )
    
    evaluator = CompanyQualityEvaluator()
    
    for i, goal in enumerate(research_goals, 1):
        print(f"\n📋 Test Case {i}: {goal}")
        try:
            result = await evaluator.evaluate_single_company(standard_finding, goal)
            print(f"   Quality: {result.quality_score:.2f} | Coverage: {result.coverage_score:.2f}")
            print(f"   Gaps: {len(result.gaps)} | Issues: {len(result.evidence_issues)}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

async def test_edge_cases():
    """Test edge cases for quality evaluator"""
    print("\n🧪 Testing Edge Cases")
    print("=" * 50)
    
    evaluator = CompanyQualityEvaluator()
    
    # Edge case 1: Empty evidence
    empty_finding = create_mock_finding(
        domain="empty.com",
        confidence_score=0.5,
        evidence_sources=0,
        goal_achieved=False,
        technologies=[],
        evidences=[]
    )
    
    print("\n📋 Edge Case 1: Empty Evidence")
    try:
        result = await evaluator.evaluate_single_company(empty_finding, "Find companies using AI")
        print(f"✅ Quality Score: {result.quality_score:.2f}")
        print(f"✅ Coverage Score: {result.coverage_score:.2f}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Edge case 2: Very high confidence but poor evidence
    poor_evidence_finding = create_mock_finding(
        domain="poor.com",
        confidence_score=0.95,
        evidence_sources=1,
        goal_achieved=True,
        technologies=["AI"],
        evidences=["Company uses AI"]
    )
    
    print("\n📋 Edge Case 2: High Confidence, Poor Evidence")
    try:
        result = await evaluator.evaluate_single_company(poor_evidence_finding, "Find companies using AI")
        print(f"✅ Quality Score: {result.quality_score:.2f}")
        print(f"✅ Coverage Score: {result.coverage_score:.2f}")
    except Exception as e:
        print(f"❌ Failed: {e}")

async def main():
    """Run all quality evaluator tests"""
    print("🚀 Testing Quality Evaluator Agent")
    print("=" * 60)
    
    # Test individual company evaluation
    await test_company_quality_evaluator()
    
    # Test aggregation
    await test_quality_evaluator_aggregation()
    
    # Test different research goals
    await test_different_research_goals()
    
    # Test edge cases
    await test_edge_cases()
    
    print("\n✅ Quality Evaluator Agent Tests Completed!")
    print("💡 The agent should provide comprehensive quality and coverage analysis")

if __name__ == "__main__":
    asyncio.run(main()) 