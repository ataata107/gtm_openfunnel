#!/usr/bin/env python3
"""
Test Script to Show Detailed Logs

This script demonstrates the detailed logging functionality
by running a simplified version of the GTM workflow.
Located in tests/ folder for better organization.
"""

import logging
import time
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gtm_workflow.log')
    ]
)

logger = logging.getLogger(__name__)

def simulate_gtm_workflow():
    """Simulate the GTM workflow with detailed logging"""
    
    logger.info("=" * 80)
    logger.info("🚀 GTM INTELLIGENCE SYSTEM - WORKFLOW SIMULATION")
    logger.info("=" * 80)
    
    # Simulate research request
    research_goal = "Find fintech companies using AI for fraud detection"
    logger.info(f"📋 Research Goal: {research_goal}")
    logger.info(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Query Agent
    logger.info("\n" + "=" * 60)
    logger.info("🔍 QUERY AGENT: Starting search strategy generation...")
    logger.info("🤖 Invoking LLM for strategy generation...")
    time.sleep(2)  # Simulate LLM processing
    
    strategies = [
        "fintech AI fraud detection companies",
        "machine learning fraud prevention fintech",
        "AI-powered fraud detection fintech startups",
        "fraud detection algorithms fintech",
        "fintech companies using AI for security",
        "artificial intelligence fraud detection payments",
        "ML fraud detection fintech solutions",
        "AI fraud prevention fintech companies",
        "fraud detection technology fintech",
        "machine learning security fintech"
    ]
    
    logger.info(f"✅ QUERY AGENT: Generated {len(strategies)} search strategies")
    for i, strategy in enumerate(strategies, 1):
        logger.info(f"   {i}. {strategy}")
    
    # Step 2: Company Aggregator
    logger.info("\n" + "=" * 60)
    logger.info("🏢 COMPANY AGGREGATOR: Starting company extraction...")
    logger.info("🔍 Running Serper and extracting companies using GPT-4o-mini...")
    time.sleep(3)  # Simulate API calls
    
    companies = [
        {"name": "Stripe", "domain": "stripe.com", "source": "serper_search"},
        {"name": "Square", "domain": "square.com", "source": "serper_search"},
        {"name": "Plaid", "domain": "plaid.com", "source": "serper_search"},
        {"name": "Adyen", "domain": "adyen.com", "source": "serper_search"},
        {"name": "Checkout.com", "domain": "checkout.com", "source": "serper_search"}
    ]
    
    logger.info(f"✅ COMPANY AGGREGATOR: Extracted {len(companies)} companies")
    for company in companies:
        logger.info(f"   - {company['name']} ({company['domain']}) — Source: {company['source']}")
    
    # Step 3: Multi-Source Search
    logger.info("\n" + "=" * 60)
    logger.info("🔍 MULTI-SOURCE SEARCH: Starting parallel search execution...")
    logger.info(f"⚡ Max Parallel Searches: 20")
    logger.info(f"🎯 Target Companies: {len(companies)}")
    
    search_results = {}
    for company in companies:
        logger.info(f"🔍 Searching for {company['domain']}...")
        time.sleep(0.5)  # Simulate search time
        search_results[company['domain']] = [
            f"Found evidence of AI fraud detection at {company['domain']}",
            f"Machine learning models used for transaction analysis",
            f"Real-time fraud detection with AI algorithms"
        ]
        logger.info(f"   ✅ Found {len(search_results[company['domain']])} evidence snippets")
    
    # Step 4: Website Scraper
    logger.info("\n" + "=" * 60)
    logger.info("🌐 WEBSITE SCRAPER: Starting website content extraction...")
    
    website_results = {}
    for company in companies:
        logger.info(f"🌐 Scraping {company['domain']}...")
        time.sleep(0.3)  # Simulate scraping time
        website_results[company['domain']] = [
            f"Company website mentions AI-powered fraud detection",
            f"Technology stack includes machine learning models",
            f"Security features include real-time fraud prevention"
        ]
        logger.info(f"   ✅ Extracted {len(website_results[company['domain']])} website snippets")
    
    # Step 5: Evaluator
    logger.info("\n" + "=" * 60)
    logger.info("🧠 EVALUATOR: Starting evidence evaluation...")
    
    findings = []
    for company in companies:
        logger.info(f"🧠 Evaluating {company['domain']}...")
        time.sleep(0.5)  # Simulate evaluation time
        
        # Simulate confidence scoring
        confidence = 0.85 + (hash(company['domain']) % 15) / 100  # Pseudo-random confidence
        
        finding = {
            "domain": company['domain'],
            "confidence_score": confidence,
            "evidence_sources": len(search_results.get(company['domain'], [])) + len(website_results.get(company['domain'], [])),
            "findings": {
                "ai_fraud_detection": True,
                "technologies": ["TensorFlow", "scikit-learn", "PyTorch"],
                "evidence": search_results.get(company['domain'], []) + website_results.get(company['domain'], []),
                "signals_found": len(search_results.get(company['domain'], [])) + len(website_results.get(company['domain'], []))
            },
            "signals_found": len(search_results.get(company['domain'], [])) + len(website_results.get(company['domain'], []))
        }
        findings.append(finding)
        
        logger.info(f"   ✅ {company['domain']}: {confidence:.2f} confidence, {finding['evidence_sources']} evidence sources")
    
    # Step 6: Quality Evaluator
    logger.info("\n" + "=" * 60)
    logger.info("📊 QUALITY EVALUATOR: Starting quality analysis...")
    
    total_evidence = sum(len(search_results[domain]) + len(website_results[domain]) for domain in search_results)
    avg_confidence = sum(f['confidence_score'] for f in findings) / len(findings)
    coverage_score = min(len(companies) / 10, 1.0)  # Assume target is 10 companies
    
    logger.info(f"📊 Quality Metrics:")
    logger.info(f"   - Total Evidence Sources: {total_evidence}")
    logger.info(f"   - Average Confidence: {avg_confidence:.2f}")
    logger.info(f"   - Coverage Score: {coverage_score:.2f}")
    logger.info(f"   - Companies Evaluated: {len(companies)}")
    
    # Step 7: Strategy Refinement
    logger.info("\n" + "=" * 60)
    logger.info("🔄 STRATEGY REFINEMENT: Analyzing gaps and refining strategies...")
    
    if coverage_score < 0.8:
        logger.info("⚠️ Coverage below threshold, generating refined strategies...")
        refined_strategies = [
            "fintech AI fraud detection 2024",
            "machine learning fraud prevention companies",
            "AI fraud detection startups fintech"
        ]
        logger.info(f"✅ Generated {len(refined_strategies)} refined strategies")
        for i, strategy in enumerate(refined_strategies, 1):
            logger.info(f"   {i}. {strategy}")
    else:
        logger.info("✅ Coverage threshold met, no refinement needed")
    
    # Final Results
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESEARCH RESULTS SUMMARY")
    logger.info("=" * 40)
    logger.info(f"🔍 Search Strategies Generated: {len(strategies)}")
    logger.info(f"🏢 Companies Extracted: {len(companies)}")
    logger.info(f"📋 Final Findings: {len(findings)}")
    logger.info(f"🔍 Total Searches Executed: {sum(len(search_results[domain]) for domain in search_results)}")
    logger.info(f"🌐 Website Scrapes: {sum(len(website_results[domain]) for domain in website_results)}")
    
    logger.info("\n🏢 Extracted Companies:")
    for company in companies:
        logger.info(f"   - {company['name']} ({company['domain']})")
    
    logger.info("\n📋 Company Findings:")
    for finding in findings:
        logger.info(f"   - {finding['domain']}: {finding['confidence_score']:.2f} confidence")
    
    logger.info("\n📈 PERFORMANCE METRICS")
    logger.info("=" * 30)
    processing_time = 15  # Simulated processing time
    logger.info(f"⏱️ Processing Time: {processing_time}s")
    logger.info(f"🔍 Queries/Second: {len(strategies) / processing_time:.1f}")
    logger.info(f"💾 Cache Hit Rate: 0.0")
    logger.info(f"❌ Failed Requests: 0")
    
    logger.info("\n✅ Research completed successfully!")
    logger.info("=" * 80)
    
    return {
        "research_goal": research_goal,
        "total_companies": len(companies),
        "search_strategies_generated": len(strategies),
        "total_searches_executed": sum(len(search_results[domain]) for domain in search_results),
        "processing_time_ms": processing_time * 1000,
        "company_domains": [company['domain'] for company in companies],
        "results": findings,
        "search_performance": {
            "queries_per_second": len(strategies) / processing_time,
            "cache_hit_rate": 0.0,
            "failed_requests": 0
        }
    }

def main():
    """Main function to run the workflow simulation"""
    print("🧪 GTM Workflow Logging Test")
    print("=" * 50)
    
    try:
        results = simulate_gtm_workflow()
        
        print("\n🎉 Workflow simulation completed!")
        print(f"📊 Results: {results['total_companies']} companies, {results['search_strategies_generated']} strategies")
        print(f"📝 Log file: gtm_workflow.log")
        
    except Exception as e:
        logger.error(f"❌ Workflow simulation failed: {e}")

if __name__ == "__main__":
    main() 