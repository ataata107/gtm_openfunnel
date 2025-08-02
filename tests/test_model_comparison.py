#!/usr/bin/env python3
"""
Test to compare performance between gpt-4o-mini and gpt-3.5-turbo
"""

import time
import sys
import os

# Add the parent directory to the path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List

load_dotenv()

class ExtractedCompany(BaseModel):
    name: str = Field(..., description="Company name")
    domain: str = Field(..., description="Company domain (e.g., stripe.com)")
    source_url: str = Field(..., description="The URL where the company was found")

class CompanyExtractionOutput(BaseModel):
    companies: List[ExtractedCompany]

def test_model_performance():
    """Compare performance between models"""
    
    print("🧪 Testing Model Performance Comparison")
    print("=" * 50)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found")
        return
    
    # Sample search result
    sample_result = """
    Title: Top AI Fraud Detection Companies in Fintech
    Snippet: Discover the leading AI fraud detection companies including Stripe, Sift, and Hawk AI that are revolutionizing financial security.
    Source URL: https://example.com/ai-fraud-detection
    
    Title: Machine Learning in Financial Fraud Prevention
    Snippet: Companies like Feedzai and Sardine are using advanced machine learning algorithms to detect fraud in real-time.
    Source URL: https://example.com/ml-fraud-prevention
    """
    
    prompt = PromptTemplate.from_template(
        """You are an expert at parsing company intelligence from web search results.

Your goal: Extract distinct companies relevant to the following research objective:

Research Goal: {research_goal}

Given the following raw text from a search engine result, extract all **unique companies** that match the research goal.
Return a list of companies with:
- Company name
- Domain (e.g., stripe.com)
- The source URL where it was mentioned

Only return a list of Pydantic models with the fields: name, domain, source_url.

Raw search result:
{search_result}
"""
    )
    
    input_text = prompt.format(
        search_result=sample_result,
        research_goal="Find fintech companies using AI for fraud detection"
    )
    
    models = [
        ("gpt-4o-mini", "GPT-4o Mini"),
        ("gpt-3.5-turbo", "GPT-3.5 Turbo")
    ]
    
    results = {}
    
    for model_name, display_name in models:
        print(f"\n⏱️  Testing {display_name}...")
        
        llm = ChatOpenAI(model=model_name, temperature=0)
        structured_llm = llm.with_structured_output(CompanyExtractionOutput)
        
        # Test 5 calls
        start_time = time.time()
        
        for i in range(5):
            try:
                result = structured_llm.invoke(input_text)
                print(f"  Call {i+1}: {len(result.companies)} companies")
            except Exception as e:
                print(f"  Call {i+1}: Error - {e}")
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        avg_ms = duration_ms / 5
        
        results[model_name] = {
            "total_ms": duration_ms,
            "avg_ms": avg_ms,
            "display_name": display_name
        }
        
        print(f"✅ {display_name}: {duration_ms:.2f}ms total, {avg_ms:.2f}ms avg")
    
    # Show comparison
    print(f"\n📊 Model Performance Comparison:")
    print("=" * 50)
    
    for model_name, result in results.items():
        print(f"{result['display_name']:15} | {result['total_ms']:8.2f}ms total | {result['avg_ms']:6.2f}ms avg")
    
    if len(results) == 2:
        gpt4_time = results["gpt-4o-mini"]["avg_ms"]
        gpt35_time = results["gpt-3.5-turbo"]["avg_ms"]
        speedup = gpt4_time / gpt35_time
        print(f"\n🚀 GPT-3.5 Turbo is {speedup:.1f}x faster than GPT-4o Mini")
    
    return results

if __name__ == "__main__":
    test_model_performance() 