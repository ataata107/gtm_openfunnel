#!/usr/bin/env python3
"""
Test script for quality_evaluator_agent performance
"""

import sys
import os
import time
import json
import asyncio
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.state import GTMState, CompanyFinding
from agents.quality_evaluator_agent import quality_evaluator_agent

load_dotenv()

def create_test_state():
    """Create a test state with sample findings"""
    
    # Sample findings from evaluator agent
    findings = [
        CompanyFinding(
            domain="stripe.com",
            confidence_score=0.9,
            evidence_sources=6,
            findings={
                "goal_achieved": True,
                "technologies": ["AI", "Machine Learning", "Real-time Analysis", "Fraud Detection", "Payment Processing"],
                "evidences": [
                    "Stripe uses AI and machine learning for fraud detection in payment processing",
                    "Their systems analyze transaction patterns in real-time to identify suspicious activity",
                    "Stripe's fraud detection capabilities include advanced algorithms",
                    "The company has implemented AI-powered fraud prevention tools",
                    "Stripe's AI-powered fraud detection helps merchants reduce fraud losses"
                ],
                "confidence_level": "High",
                "research_goal": "AI-powered fraud detection in fintech"
            },
            signals_found=7
        ),
        CompanyFinding(
            domain="sift.com",
            confidence_score=0.9,
            evidence_sources=6,
            findings={
                "goal_achieved": True,
                "technologies": ["AI", "Machine Learning", "Behavioral Analysis", "Device Fingerprinting", "Real-time Monitoring", "E-commerce", "Fintech"],
                "evidences": [
                    "Sift provides AI-powered fraud detection solutions for e-commerce and fintech companies",
                    "Their platform uses machine learning to identify fraudulent transactions",
                    "Sift's fraud detection system analyzes user behavior patterns and transaction data",
                    "The company offers comprehensive fraud prevention tools including device fingerprinting",
                    "Sift offers real-time fraud prevention with customizable rules"
                ],
                "confidence_level": "High",
                "research_goal": "AI-powered fraud detection in fintech"
            },
            signals_found=6
        ),
        CompanyFinding(
            domain="hawk.ai",
            confidence_score=0.9,
            evidence_sources=6,
            findings={
                "goal_achieved": True,
                "technologies": ["AI", "Machine Learning", "Cloud-based", "Financial Institutions", "Real-time Monitoring", "Advanced Analytics"],
                "evidences": [
                    "Hawk AI specializes in AI-driven fraud detection for financial institutions",
                    "Their platform uses advanced machine learning algorithms",
                    "Hawk AI's fraud detection system provides real-time monitoring and alerting",
                    "The company offers cloud-based fraud prevention solutions with high accuracy rates",
                    "Hawk AI's machine learning algorithms can detect fraud patterns across multiple channels"
                ],
                "confidence_level": "High",
                "research_goal": "AI-powered fraud detection in fintech"
            },
            signals_found=7
        ),
        CompanyFinding(
            domain="feedzai.com",
            confidence_score=0.9,
            evidence_sources=6,
            findings={
                "goal_achieved": True,
                "technologies": ["AI", "Machine Learning", "Behavioral Analysis", "Risk Scoring", "Real-time Monitoring", "Banks", "Financial Services"],
                "evidences": [
                    "Feedzai develops AI-powered fraud detection software for banks and financial services",
                    "Their platform uses machine learning for real-time transaction monitoring",
                    "Feedzai's fraud detection capabilities include behavioral analysis and risk scoring",
                    "The company provides comprehensive fraud prevention tools with advanced analytics",
                    "Feedzai's platform uses machine learning to identify fraudulent transactions"
                ],
                "confidence_level": "High",
                "research_goal": "AI-powered fraud detection in fintech"
            },
            signals_found=7
        ),
        CompanyFinding(
            domain="sardine.ai",
            confidence_score=0.9,
            evidence_sources=6,
            findings={
                "goal_achieved": True,
                "technologies": ["AI", "Machine Learning", "Fintech", "Digital Payments", "Real-time Detection", "Behavioral Analysis"],
                "evidences": [
                    "Sardine AI offers fraud detection solutions for fintech companies using artificial intelligence",
                    "Sardine's platform provides real-time fraud detection with high accuracy and low latency",
                    "The company specializes in AI-powered fraud prevention for digital payments",
                    "Sardine's fraud prevention tools include behavioral analysis and risk-based authentication",
                    "Sardine AI provides fraud detection solutions specifically designed for fintech companies"
                ],
                "confidence_level": "High",
                "research_goal": "AI-powered fraud detection in fintech"
            },
            signals_found=6
        )
    ]
    
    return GTMState(
        research_goal="AI-powered fraud detection in fintech",
        final_findings=findings,
        max_parallel_searches=10,
        iteration_count=1,
        max_iterations=2
    )

def test_quality_evaluator_agent():
    """Test the quality evaluator agent performance"""
    
    print("🧪 Testing Quality Evaluator Agent Performance")
    print("=" * 55)
    
    # Check environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        return
    
    print("✅ Environment variables found")
    
    # Create test state
    test_state = create_test_state()
    print(f"📝 Created test state with {len(test_state.final_findings)} findings")
    
    # Time the quality evaluation
    print("\n⏱️  Starting performance test...")
    start_time = time.time()
    
    try:
        # Run the quality evaluator agent
        result_state = quality_evaluator_agent(test_state)
        
        end_time = time.time()
        total_duration = (end_time - start_time) * 1000
        
        print(f"\n📊 Performance Results:")
        print(f"  ⏱️  Total Time: {total_duration/1000:.2f}s ({total_duration:.2f}ms)")
        print(f"  🏢 Companies Analyzed: {len(test_state.final_findings)}")
        print(f"  📝 Total Evidence Sources: {sum(f.evidence_sources for f in test_state.final_findings)}")
        
        if result_state.quality_metrics:
            quality_metrics = result_state.quality_metrics
            print(f"  📊 Coverage Score: {quality_metrics.get('coverage_score', 0):.2f}")
            print(f"  📊 Quality Score: {quality_metrics.get('quality_score', 0):.2f}")
            print(f"  📊 Missing Aspects: {len(quality_metrics.get('missing_aspects', []))}")
            print(f"  📊 Coverage Gaps: {len(quality_metrics.get('coverage_gaps', []))}")
            print(f"  📊 Evidence Issues: {len(quality_metrics.get('evidence_issues', []))}")
            print(f"  📊 Recommendations: {len(quality_metrics.get('recommendations', []))}")
        
        # Save test results
        os.makedirs("../debug_output", exist_ok=True)
        output_path = os.path.join("../debug_output", "quality_evaluator_test_results.json")
        
        test_results = {
            "total_time_ms": total_duration,
            "total_time_s": total_duration / 1000,
            "companies_analyzed": len(test_state.final_findings),
            "total_evidence_sources": sum(f.evidence_sources for f in test_state.final_findings),
            "quality_metrics": result_state.quality_metrics if result_state.quality_metrics else {}
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        print(f"📁 Saved test results to {output_path}")
        print(f"\n✅ Performance testing completed!")
        print(f"Performance: {total_duration:.2f}ms for {len(test_state.final_findings)} companies")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_quality_evaluator_agent() 