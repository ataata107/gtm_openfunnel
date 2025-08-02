import asyncio
import os
import json
import re
from firecrawl import AsyncFirecrawlApp, FirecrawlApp
from pydantic import BaseModel
from graph.state import GTMState
from dotenv import load_dotenv

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")


# Define schema for relevant snippet extraction
class RelevantSnippetSchema(BaseModel):
    relevant_snippets: list[str]
    relevance_score: float


async def extract_relevant_snippets(app: AsyncFirecrawlApp, domain: str, research_goal: str, sem: asyncio.Semaphore) -> tuple:
    """Extract snippets relevant to the research goal from a website"""
    async with sem:
        try:
            # Use FireCrawl's extract API to find relevant content
            extract_app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
            
            # Create a prompt that focuses on the research goal
            prompt = f"""
            Analyze the website content and extract snippets that are directly relevant to this research goal: "{research_goal}"
            
            Look for:
            1. Specific mentions or evidence related to the research goal
            2. Technologies, features, or capabilities that align with the goal
            3. Case studies, examples, or descriptions that demonstrate relevance
            4. Any quantitative data or metrics related to the goal
            
            Focus on extracting concrete, factual snippets that provide evidence for or against the research goal.
            """
            
            # Start async extraction
            extract_job = extract_app.async_extract(
                urls=[f"https://{domain}"],
                prompt=prompt,
                schema=RelevantSnippetSchema.model_json_schema()
            )
            
            # Poll for completion
            max_attempts = 30
            attempt = 0
            
            while attempt < max_attempts:
                attempt += 1
                job_status = extract_app.get_extract_status(extract_job.id)
                
                if job_status.status == 'completed':
                    if job_status.success and job_status.data:
                        # Extract the relevant snippets
                        result = job_status.data[0] if isinstance(job_status.data, list) else job_status.data
                        snippets = result.get('relevant_snippets', [])
                        relevance_score = result.get('relevance_score', 0.0)
                        
                        return domain, {
                            'snippets': snippets,
                            'relevance_score': relevance_score,
                            'research_goal': research_goal
                        }
                    else:
                        return domain, {
                            'snippets': [],
                            'relevance_score': 0.0,
                            'research_goal': research_goal,
                            'error': 'No relevant content found'
                        }
                elif job_status.status in ['failed', 'cancelled']:
                    return domain, {
                        'snippets': [],
                        'relevance_score': 0.0,
                        'research_goal': research_goal,
                        'error': f'Extraction {job_status.status}: {job_status.error}'
                    }
                else:
                    await asyncio.sleep(2)  # Wait 2 seconds before next check
            
            # Timeout
            return domain, {
                'snippets': [],
                'relevance_score': 0.0,
                'research_goal': research_goal,
                'error': 'Extraction timed out'
            }
            
        except Exception as e:
            return domain, {
                'snippets': [],
                'relevance_score': 0.0,
                'research_goal': research_goal,
                'error': f'Error extracting from {domain}: {str(e)}'
            }


def website_scraper_agent(state: GTMState) -> GTMState:
    if not state.extracted_companies:
        raise ValueError("No companies to scrape")

    print(f"🔍 Found {len(state.extracted_companies)} companies to analyze:")
    # for company in state.extracted_companies:
    #     print(f"  - {company.domain}")
    
    print(f"🎯 Research Goal: {state.research_goal}")

    async def run_all():
        sem = asyncio.Semaphore(state.max_parallel_searches)
        app = AsyncFirecrawlApp(api_key=FIRECRAWL_API_KEY)

        tasks = [
            extract_relevant_snippets(app, company.domain, state.research_goal, sem) 
            for company in state.extracted_companies
        ]
        results = await asyncio.gather(*tasks)

        return dict(results)

    print("🌐 Extracting relevant snippets from company websites...")
    website_results = asyncio.run(run_all())

    # ✅ Save to disk for debugging
    os.makedirs("debug_output", exist_ok=True)
    output_path = os.path.join("debug_output", "relevant_snippets_output.json")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(website_results, f, ensure_ascii=False, indent=2)
        print(f"📁 Saved relevant snippets to {output_path}")
    except Exception as e:
        print(f"⚠️ Failed to write relevant snippets: {e}")

    # ✅ Process and merge into state
    merged = dict(state.search_results_website or {})
    for domain, result in website_results.items():
        if 'error' not in result:
            # Keep snippets as separate items for better evaluation
            if result['snippets']:
                merged.setdefault(domain, []).extend(result['snippets'])
            else:
                merged.setdefault(domain, []).append("No relevant snippets found")
        else:
            merged.setdefault(domain, []).append(f"Error: {result['error']}")

    return state.model_copy(update={"search_results_website": merged})
