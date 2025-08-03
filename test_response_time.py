#!/usr/bin/env python3
"""
Test response time for quality evaluator agent and overall system performance
"""

import asyncio
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.quality_evaluator_agent import CompanyQualityEvaluator, QualityEvaluator
from graph.state import GTMState, CompanyFinding
from typing import List

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

async def test_quality_evaluator_response_time():
    """Test response time for quality evaluator"""
    print("⏱️ Testing Quality Evaluator Response Time")
    print("=" * 50)
    
    evaluator = CompanyQualityEvaluator()
    
    # Create test data
    test_finding = create_mock_finding(
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
    
    # Test single company evaluation response time
    print("\n📋 Test 1: Single Company Evaluation")
    start_time = time.time()
    
    try:
        result = await evaluator.evaluate_single_company(test_finding, "Find fintech companies using AI for fraud detection")
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"✅ Response Time: {response_time:.2f}ms")
        print(f"✅ Quality Score: {result.quality_score:.2f}")
        print(f"✅ Coverage Score: {result.coverage_score:.2f}")
        
        if response_time < 5000:  # 5 seconds
            print("✅ Performance: EXCELLENT (< 5s)")
        elif response_time < 10000:  # 10 seconds
            print("✅ Performance: GOOD (5-10s)")
        else:
            print("⚠️ Performance: SLOW (> 10s)")
            
    except Exception as e:
        print(f"❌ Failed: {e}")

async def test_aggregation_response_time():
    """Test response time for aggregation"""
    print("\n📋 Test 2: Aggregation Response Time")
    
    evaluator = QualityEvaluator()
    
    # Create multiple test findings
    findings = [
        create_mock_finding("stripe.com", 0.92, 15, True, ["AI", "ML"], ["Evidence 1", "Evidence 2"]),
        create_mock_finding("square.com", 0.75, 10, True, ["AI"], ["Evidence 3"]),
        create_mock_finding("paypal.com", 0.85, 12, True, ["ML"], ["Evidence 4", "Evidence 5"]),
        create_mock_finding("stripe.com", 0.78, 8, True, ["AI"], ["Evidence 6"])
    ]
    
    state = create_mock_state("Find fintech companies using AI for fraud detection", findings)
    
    start_time = time.time()
    
    try:
        result = await evaluator.analyze_coverage_and_quality_parallel(state)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"✅ Response Time: {response_time:.2f}ms")
        print(f"✅ Quality Score: {result.quality_score:.2f}")
        print(f"✅ Coverage Score: {result.coverage_score:.2f}")
        print(f"✅ Companies Analyzed: {len(findings)}")
        
        if response_time < 15000:  # 15 seconds
            print("✅ Performance: EXCELLENT (< 15s)")
        elif response_time < 30000:  # 30 seconds
            print("✅ Performance: GOOD (15-30s)")
        else:
            print("⚠️ Performance: SLOW (> 30s)")
            
    except Exception as e:
        print(f"❌ Failed: {e}")

async def test_batch_performance():
    """Test performance with different batch sizes"""
    print("\n📋 Test 3: Batch Performance Testing")
    
    evaluator = QualityEvaluator()
    
    # Test different batch sizes
    batch_sizes = [5, 10, 20, 50]
    
    for batch_size in batch_sizes:
        print(f"\n🔍 Testing batch size: {batch_size} companies")
        
        # Create batch of findings
        findings = []
        for i in range(batch_size):
            findings.append(create_mock_finding(
                f"company{i}.com",
                0.8,
                10,
                True,
                ["AI", "ML"],
                [f"Evidence {i+1}", f"Evidence {i+2}"]
            ))
        
        state = create_mock_state("Find fintech companies using AI for fraud detection", findings)
        
        start_time = time.time()
        
        try:
            result = await evaluator.analyze_coverage_and_quality_parallel(state)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            print(f"   ⏱️ Response Time: {response_time:.2f}ms")
            print(f"   📊 Quality Score: {result.quality_score:.2f}")
            print(f"   📈 Coverage Score: {result.coverage_score:.2f}")
            
            # Performance assessment
            if response_time < batch_size * 1000:  # 1 second per company
                print(f"   ✅ Performance: EXCELLENT")
            elif response_time < batch_size * 2000:  # 2 seconds per company
                print(f"   ✅ Performance: GOOD")
            else:
                print(f"   ⚠️ Performance: SLOW")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")

async def main():
    """Run all performance tests"""
    print("🚀 Quality Evaluator Performance Tests")
    print("=" * 50)
    
    await test_quality_evaluator_response_time()
    await test_aggregation_response_time()
    await test_batch_performance()
    
    print("\n🎉 Performance tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 