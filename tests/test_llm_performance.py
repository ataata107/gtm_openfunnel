#!/usr/bin/env python3
"""
Test script to measure LLM call performance in isolation.
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

def test_llm_performance():
    """Test how long a single LLM call takes"""
    
    print("🧪 Testing LLM Performance")
    print("=" * 40)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found")
        return
    
    # Create LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(CompanyExtractionOutput)
    
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
    
    # Sample search result
    sample_result = """
    Title: Top AI Fraud Detection Companies in Fintech
    Snippet: Discover the leading AI fraud detection companies including Stripe, Sift, and Hawk AI that are revolutionizing financial security.
    Source URL: https://example.com/ai-fraud-detection
    
    Title: Machine Learning in Financial Fraud Prevention
    Snippet: Companies like Feedzai and Sardine are using advanced machine learning algorithms to detect fraud in real-time.
    Source URL: https://example.com/ml-fraud-prevention
    """
    
    print("⏱️  Testing single LLM call...")
    start_time = time.time()
    
    try:
        input_text = prompt.format(
            search_result=sample_result,
            research_goal="Find fintech companies using AI for fraud detection"
        )
        
        result = structured_llm.invoke(input_text)
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        print(f"✅ Single LLM call took: {duration_ms:.2f}ms")
        print(f"📊 Extracted {len(result.companies)} companies")
        
        # Test multiple calls
        print(f"\n⏱️  Testing 10 LLM calls sequentially...")
        start_time = time.time()
        
        for i in range(10):
            result = structured_llm.invoke(input_text)
            print(f"  Call {i+1}: {len(result.companies)} companies")
        
        end_time = time.time()
        total_duration_ms = (end_time - start_time) * 1000
        avg_duration_ms = total_duration_ms / 10
        
        print(f"✅ 10 sequential LLM calls took: {total_duration_ms:.2f}ms")
        print(f"📊 Average per call: {avg_duration_ms:.2f}ms")
        
        return {
            "single_call_ms": duration_ms,
            "ten_calls_ms": total_duration_ms,
            "avg_call_ms": avg_duration_ms
        }
        
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return None

if __name__ == "__main__":
    results = test_llm_performance()
    if results:
        print(f"\n📊 Summary:")
        print(f"  Single call: {results['single_call_ms']:.2f}ms")
        print(f"  10 calls: {results['ten_calls_ms']:.2f}ms")
        print(f"  Average: {results['avg_call_ms']:.2f}ms") 