#!/usr/bin/env python3
"""
Test script for Quality Evaluator Agent
"""

import os
import json
import sys
from dotenv import load_dotenv
from graph.state import GTMState, CompanyFinding
from agents.quality_evaluator_agent import quality_evaluator_agent

load_dotenv()

def create_test_state():
    """Create a test state with sample findings"""
    
    # Sample findings
    findings = [
        CompanyFinding(
            domain="stripe.com",
            confidence_score=0.9,
            evidence_sources=15,
            findings={
                "goal_achieved": True,
                "technologies": ["TensorFlow", "scikit-learn", "AI/ML"],
                "evidences": [
                    "Stripe uses AI for fraud detection in real-time",
                    "Machine learning models analyze transaction patterns",
                    "Advanced algorithms detect suspicious activity"
                ],
                "confidence_level": "High",
                "research_goal": "Find fintech companies using AI for fraud detection"
            },
            signals_found=8
        ),
        CompanyFinding(
            domain="square.com",
            confidence_score=0.7,
            evidence_sources=8,
            findings={
                "goal_achieved": True,
                "technologies": ["AI", "Machine Learning"],
                "evidences": [
                    "Square implements AI-powered fraud detection",
                    "Uses machine learning for transaction analysis"
                ],
                "confidence_level": "Medium",
                "research_goal": "Find fintech companies using AI for fraud detection"
            },
            signals_found=5
        ),
        CompanyFinding(
            domain="paypal.com",
            confidence_score=0.6,
            evidence_sources=6,
            findings={
                "goal_achieved": False,
                "technologies": ["Basic fraud detection"],
                "evidences": [
                    "PayPal has basic fraud detection systems",
                    "Limited AI implementation in fraud prevention"
                ],
                "confidence_level": "Low",
                "research_goal": "Find fintech companies using AI for fraud detection"
            },
            signals_found=3
        )
    ]
    
    state = GTMState(
        research_goal="Find fintech companies using AI for fraud detection",
        extracted_companies=[
            {"name": "Stripe", "domain": "stripe.com"},
            {"name": "Square", "domain": "square.com"},
            {"name": "PayPal", "domain": "paypal.com"}
        ],
        final_findings=findings,
        max_parallel_searches=5,
        confidence_threshold=0.8
    )
    
    return state

def test_quality_evaluator_agent():
    """Test the quality evaluator agent"""
    
    print("🧪 Testing Quality Evaluator Agent...")
    
    # Create test state
    state = create_test_state()
    
    print(f"📊 Test State:")
    print(f"  Research Goal: {state.research_goal}")
    print(f"  Companies: {len(state.extracted_companies)}")
    print(f"  Findings: {len(state.final_findings)}")
    
    # Run quality evaluator
    try:
        updated_state = quality_evaluator_agent(state)
        
        print(f"\n✅ Quality Evaluation Completed!")
        print(f"📈 Quality Metrics:")
        print(f"  Coverage Score: {updated_state.quality_metrics.get('coverage_score', 'N/A')}")
        print(f"  Quality Score: {updated_state.quality_metrics.get('quality_score', 'N/A')}")
        print(f"  Missing Aspects: {len(updated_state.quality_metrics.get('missing_aspects', []))}")
        print(f"  Coverage Gaps: {len(updated_state.quality_metrics.get('coverage_gaps', []))}")
        
        # Check if quality_analysis.json was created
        if os.path.exists("debug_output/quality_analysis.json"):
            print(f"📁 Quality analysis saved to debug_output/quality_analysis.json")
        
    except Exception as e:
        print(f"❌ Quality evaluation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_quality_evaluator_agent() 