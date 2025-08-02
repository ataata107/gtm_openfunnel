#!/usr/bin/env python3
"""
Test script to use FireCrawl async extract API with status checking
"""

import os
import time
from firecrawl import FirecrawlApp
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# Define a schema to extract relevant evidence about AI use
class ExtractSchema(BaseModel):
    uses_ai: bool
    ai_evidence_snippet: str

def test_async_extract_api():
    """Test FireCrawl async extract API with status checking"""
    
    if not FIRECRAWL_API_KEY:
        print("❌ FIRECRAWL_API_KEY not found in environment variables")
        return
    
    print("🔍 Testing FireCrawl async extract API with stripe.com...")
    
    try:
        app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
        
        # Start an async extraction job
        print("📡 Starting async extract job...")
        extract_job = app.async_extract(
            urls=['https://stripe.com'],
            prompt="Extract if the company uses artificial intelligence and provide a short snippet as evidence.",
            schema=ExtractSchema.model_json_schema()
        )
        
        print(f"✅ Job started! Job ID: {extract_job.id}")
        print(f"📋 Initial status: {extract_job.status}")
        
        # Poll for completion
        max_attempts = 30  # 30 seconds max
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            print(f"\n🔄 Checking status (attempt {attempt}/{max_attempts})...")
            
            job_status = app.get_extract_status(extract_job.id)
            print(f"📊 Status: {job_status.status}")
            print(f"✅ Success: {job_status.success}")
            
            if job_status.status == 'completed':
                print("🎉 Job completed successfully!")
                if job_status.success and job_status.data:
                    print(f"\n🎯 Extracted Data:")
                    print(f"  Uses AI: {job_status.data.get('uses_ai', 'N/A')}")
                    print(f"  Evidence: {job_status.data.get('ai_evidence_snippet', 'N/A')}")
                break
            elif job_status.status == 'failed':
                print("❌ Job failed!")
                if job_status.error:
                    print(f"Error: {job_status.error}")
                break
            elif job_status.status == 'cancelled':
                print("❌ Job was cancelled!")
                break
            else:
                print("⏳ Job still processing...")
                time.sleep(1)  # Wait 1 second before next check
        else:
            print("⏰ Timeout: Job took too long to complete")
            
    except Exception as e:
        print(f"❌ Error during async extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_async_extract_api()
