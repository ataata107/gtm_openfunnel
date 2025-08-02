#!/usr/bin/env python3
"""
Test script for evaluator_agent performance
"""

import sys
import os
import time
import json
import asyncio
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.state import GTMState, CompanyMeta
from agents.evaluator_agent import evaluator_agent

load_dotenv()

def create_test_state():
    """Create a test state with sample companies and search results"""
    
    # Sample companies
    companies = [
        CompanyMeta(name="Stripe", domain="stripe.com", source_url="https://stripe.com"),
        CompanyMeta(name="Sift", domain="sift.com", source_url="https://sift.com"),
        CompanyMeta(name="Hawk AI", domain="hawk.ai", source_url="https://hawk.ai"),
        CompanyMeta(name="Feedzai", domain="feedzai.com", source_url="https://feedzai.com"),
        CompanyMeta(name="Sardine", domain="sardine.ai", source_url="https://sardine.ai")
    ]
    
    # Sample search results for each company
    search_results_serper = {
        "stripe.com": [
            "Stripe uses AI and machine learning for fraud detection in payment processing. Their systems analyze transaction patterns in real-time to identify suspicious activity.",
            "Stripe's fraud detection capabilities include advanced algorithms that can detect fraudulent transactions with high accuracy.",
            "The company has implemented AI-powered fraud prevention tools that help merchants reduce chargebacks and fraud losses."
        ],
        "sift.com": [
            "Sift provides AI-powered fraud detection solutions for e-commerce and fintech companies. Their platform uses machine learning to identify fraudulent transactions.",
            "Sift's fraud detection system analyzes user behavior patterns and transaction data to detect anomalies in real-time.",
            "The company offers comprehensive fraud prevention tools including device fingerprinting and behavioral analysis."
        ],
        "hawk.ai": [
            "Hawk AI specializes in AI-driven fraud detection for financial institutions. Their platform uses advanced machine learning algorithms.",
            "Hawk AI's fraud detection system provides real-time monitoring and alerting for suspicious financial activities.",
            "The company offers cloud-based fraud prevention solutions with high accuracy rates and low false positives."
        ],
        "feedzai.com": [
            "Feedzai develops AI-powered fraud detection software for banks and financial services. Their platform uses machine learning for real-time transaction monitoring.",
            "Feedzai's fraud detection capabilities include behavioral analysis and risk scoring for financial transactions.",
            "The company provides comprehensive fraud prevention tools with advanced analytics and reporting features."
        ],
        "sardine.ai": [
            "Sardine AI offers fraud detection solutions for fintech companies using artificial intelligence and machine learning.",
            "Sardine's platform provides real-time fraud detection with high accuracy and low latency for financial transactions.",
            "The company specializes in AI-powered fraud prevention for digital payments and financial services."
        ]
    }
    
    # Sample website scraping results
    search_results_website = {
        "stripe.com": [
            "Stripe's fraud detection system uses machine learning algorithms to analyze payment patterns and identify fraudulent transactions in real-time.",
            "The company offers advanced fraud prevention tools including 3D Secure authentication and risk-based authentication.",
            "Stripe's AI-powered fraud detection helps merchants reduce fraud losses and improve customer experience."
        ],
        "sift.com": [
            "Sift's AI fraud detection platform provides comprehensive protection against various types of fraud including payment fraud and account takeover.",
            "The company uses machine learning to analyze user behavior and transaction patterns for fraud detection.",
            "Sift offers real-time fraud prevention with customizable rules and automated decision-making capabilities."
        ],
        "hawk.ai": [
            "Hawk AI's fraud detection platform uses artificial intelligence to monitor financial transactions and detect suspicious activities.",
            "The company provides cloud-based fraud prevention solutions with advanced analytics and reporting capabilities.",
            "Hawk AI's machine learning algorithms can detect fraud patterns across multiple channels and payment methods."
        ],
        "feedzai.com": [
            "Feedzai's AI-powered fraud detection system provides real-time monitoring and analysis of financial transactions.",
            "The company offers comprehensive fraud prevention tools including behavioral analysis and risk scoring.",
            "Feedzai's platform uses machine learning to identify fraudulent transactions and reduce false positives."
        ],
        "sardine.ai": [
            "Sardine AI provides fraud detection solutions specifically designed for fintech companies and digital payments.",
            "The company's AI-powered platform offers real-time fraud detection with high accuracy and low latency.",
            "Sardine's fraud prevention tools include behavioral analysis and risk-based authentication for financial transactions."
        ]
    }
    
    return GTMState(
        research_goal="AI-powered fraud detection in fintech",
        extracted_companies=companies,
        search_results_serper=search_results_serper,
        search_results_website=search_results_website,
        max_parallel_searches=10,
        iteration_count=1,
        max_iterations=2
    )

def test_evaluator_agent():
    """Test the evaluator agent performance"""
    
    print("🧪 Testing Evaluator Agent Performance")
    print("=" * 50)
    
    # Check environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        return
    
    print("✅ Environment variables found")
    
    # Create test state
    test_state = create_test_state()
    print(f"📝 Created test state with {len(test_state.extracted_companies)} companies")
    
    # Time the evaluation
    print("\n⏱️  Starting performance test...")
    start_time = time.time()
    
    try:
        # Run the evaluator agent
        result_state = evaluator_agent(test_state)
        
        end_time = time.time()
        total_duration = (end_time - start_time) * 1000
        
        print(f"\n📊 Performance Results:")
        print(f"  ⏱️  Total Time: {total_duration/1000:.2f}s ({total_duration:.2f}ms)")
        print(f"  🏢 Companies Evaluated: {len(result_state.final_findings) if result_state.final_findings else 0}")
        print(f"  📝 Total Evidence Sources: {sum(f.evidence_sources for f in result_state.final_findings) if result_state.final_findings else 0}")
        
        if result_state.final_findings:
            print(f"\n🏢 Evaluation Results:")
            for i, finding in enumerate(result_state.final_findings, 1):
                confidence = finding.confidence_score
                goal_achieved = finding.findings.get("goal_achieved", False)
                technologies = finding.findings.get("technologies", [])
                signals = finding.signals_found
                
                print(f"  {i}. {finding.domain}")
                print(f"     Confidence: {confidence:.2f}")
                print(f"     Goal Achieved: {goal_achieved}")
                print(f"     Technologies: {len(technologies)} found")
                print(f"     Signals: {signals}")
                print()
        
        # Save test results
        os.makedirs("../debug_output", exist_ok=True)
        output_path = os.path.join("../debug_output", "evaluator_test_results.json")
        
        test_results = {
            "total_time_ms": total_duration,
            "total_time_s": total_duration / 1000,
            "companies_evaluated": len(result_state.final_findings) if result_state.final_findings else 0,
            "total_evidence_sources": sum(f.evidence_sources for f in result_state.final_findings) if result_state.final_findings else 0,
            "findings": [f.model_dump() for f in result_state.final_findings] if result_state.final_findings else []
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        print(f"📁 Saved test results to {output_path}")
        print(f"\n✅ Performance testing completed!")
        print(f"Performance: {total_duration:.2f}ms for {len(result_state.final_findings) if result_state.final_findings else 0} companies")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_evaluator_agent() 