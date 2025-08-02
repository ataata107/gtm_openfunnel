#!/usr/bin/env python3
"""
Test script for Strategy Refinement Agent
"""

import os
import json
import sys
from dotenv import load_dotenv
from graph.state import GTMState, CompanyFinding
from agents.strategy_refinement_agent import strategy_refinement_agent

load_dotenv()

def create_test_state_with_quality_metrics():
    """Create a test state with quality metrics for strategy refinement"""
    
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
            domain="paypal.com",
            confidence_score=0.4,
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
    
    # Sample quality metrics (from quality evaluator output)
    quality_metrics = {
        "coverage_score": 0.63,
        "quality_score": 0.68,
        "missing_aspects": [
            "Detailed case studies on AI implementation for fraud detection",
            "Quantitative metrics on fraud reduction due to AI",
            "Information on specific AI algorithms used",
            "Data on the scalability of fraud detection systems",
            "Evidence of advanced AI techniques or machine learning applications"
        ],
        "coverage_gaps": [
            "Limited coverage of PayPal's AI capabilities in fraud detection",
            "Lack of comparative analysis between companies",
            "Insufficient exploration of various types of fraud detected by AI"
        ],
        "evidence_issues": [
            "Limited quantitative data on AI effectiveness",
            "Missing recent case studies",
            "Insufficient technical depth in AI descriptions",
            "Lack of performance metrics"
        ],
        "recommendations": [
            "Conduct deeper investigations into AI capabilities of all companies",
            "Provide more detailed case studies showcasing AI's impact on fraud detection",
            "Include quantitative metrics to demonstrate effectiveness",
            "Expand on the types of fraud detected and how AI specifically addresses them",
            "Explore partnerships or collaborations with AI technology providers"
        ],
        "company_analyses": [
            {
                "company_domain": "stripe.com",
                "quality_score": 0.85,
                "coverage_score": 0.90,
                "gaps": ["Need more quantitative metrics", "Missing recent case studies"],
                "evidence_issues": ["Limited performance data"],
                "recommendations": ["Get more recent case studies", "Include performance metrics"]
            },
            {
                "company_domain": "paypal.com",
                "quality_score": 0.40,
                "coverage_score": 0.30,
                "gaps": ["Very limited AI information", "No recent AI implementation data"],
                "evidence_issues": ["Outdated information", "No technical details"],
                "recommendations": ["Research recent AI implementations", "Find technical documentation"]
            }
        ]
    }
    
    state = GTMState(
        research_goal="Find fintech companies using AI for fraud detection",
        extracted_companies=[
            {"name": "Stripe", "domain": "stripe.com"},
            {"name": "PayPal", "domain": "paypal.com"}
        ],
        final_findings=findings,
        search_strategies_generated=[
            "fintech companies AI fraud detection",
            "stripe AI fraud detection",
            "paypal fraud detection AI"
        ],
        quality_metrics=quality_metrics,
        max_parallel_searches=5,
        confidence_threshold=0.8
    )
    
    return state

def test_strategy_refinement_agent():
    """Test the strategy refinement agent"""
    
    print("🧪 Testing Strategy Refinement Agent...")
    
    # Create test state with quality metrics
    state = create_test_state_with_quality_metrics()
    
    print(f"📊 Test State:")
    print(f"  Research Goal: {state.research_goal}")
    print(f"  Companies: {len(state.extracted_companies)}")
    print(f"  Findings: {len(state.final_findings)}")
    print(f"  Quality Metrics: Available")
    print(f"  Original Strategies: {len(state.search_strategies_generated)}")
    
    # Run strategy refinement
    try:
        updated_state = strategy_refinement_agent(state)
        
        print(f"\n✅ Strategy Refinement Completed!")
        print(f"📈 Refinement Results:")
        print(f"  Total Strategies: {len(updated_state.search_strategies_generated)}")
        
        if updated_state.strategy_refinement:
            refinement = updated_state.strategy_refinement
            print(f"  Refined Strategies: {len(refinement.get('refined_strategies', []))}")
            print(f"  New Queries: {refinement.get('total_new_queries', 0)}")
            print(f"  Implementation Notes: {len(refinement.get('implementation_notes', []))}")
        
        # Check if strategy_refinement.json was created
        if os.path.exists("debug_output/strategy_refinement.json"):
            print(f"📁 Strategy refinement saved to debug_output/strategy_refinement.json")
        
    except Exception as e:
        print(f"❌ Strategy refinement failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_strategy_refinement_agent() 