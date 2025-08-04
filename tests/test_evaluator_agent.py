#!/usr/bin/env python3
"""
Test script for evaluator_agent with state save/load functionality
"""

import os
import json
import sys
from dotenv import load_dotenv
from graph.state import GTMState, CompanyMeta
from agents.evaluator_agent import evaluator_agent

# Load environment variables
load_dotenv()

def save_state(state: GTMState, filename: str = "test_state.json"):
    """Save state to a JSON file"""
    try:
        # Convert state to dict for JSON serialization
        state_dict = state.model_dump()
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(state_dict, f, indent=2, ensure_ascii=False)
        print(f"✅ State saved to {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to save state: {e}")
        return False

def load_state(filename: str = "test_state.json") -> GTMState:
    """Load state from a JSON file"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            state_dict = json.load(f)
        
        # Convert back to GTMState
        state = GTMState(**state_dict)
        print(f"✅ State loaded from {filename}")
        return state
    except Exception as e:
        print(f"❌ Failed to load state: {e}")
        return None

def load_debug_data():
    """Load real data from debug_output JSON files"""
    debug_dir = "debug_output"
    
    # Load extracted companies
    companies = []
    companies_file = os.path.join(debug_dir, "extracted_companies.json")
    if os.path.exists(companies_file):
        try:
            with open(companies_file, "r", encoding="utf-8") as f:
                companies_data = json.load(f)
                for company_data in companies_data:
                    companies.append(CompanyMeta(
                        domain=company_data["domain"],
                        name=company_data["name"],
                        industry="Fintech"  # Default industry
                    ))
            print(f"✅ Loaded {len(companies)} companies from debug data")
        except Exception as e:
            print(f"❌ Failed to load companies: {e}")
    
    # Load relevant snippets
    search_results_website = {}
    snippets_file = os.path.join(debug_dir, "relevant_snippets_output.json")
    if os.path.exists(snippets_file):
        try:
            with open(snippets_file, "r", encoding="utf-8") as f:
                snippets_data = json.load(f)
                for domain, data in snippets_data.items():
                    if "snippets" in data and data["snippets"]:
                        # Convert snippets to text format for compatibility
                        search_results_website[domain] = data["snippets"]
            print(f"✅ Loaded website snippets for {len(search_results_website)} companies")
        except Exception as e:
            print(f"❌ Failed to load snippets: {e}")
    
    # Load serper search results if available
    search_results = {}
    serper_file = os.path.join(debug_dir, "serper_search_output.json")
    if os.path.exists(serper_file):
        try:
            with open(serper_file, "r", encoding="utf-8") as f:
                serper_data = json.load(f)
                # Convert serper results to the expected format
                for query, results in serper_data.items():
                    # Extract domain from query or use a default
                    domain = query.split()[0] if query else "unknown"
                    search_results[domain] = results
            print(f"✅ Loaded serper search results for {len(search_results)} queries")
        except Exception as e:
            print(f"❌ Failed to load serper results: {e}")
    
    return companies, search_results, search_results_website

def create_test_state():
    """Create a test state using real debug data"""
    print("📁 Loading real data from debug_output...")
    
    companies, search_results, search_results_website = load_debug_data()
    
    # Use the research goal from the debug data if available
    research_goal = "Find fintech companies using AI for fraud detection"
    
    # Try to get research goal from snippets data
    snippets_file = os.path.join("debug_output", "relevant_snippets_output.json")
    if os.path.exists(snippets_file):
        try:
            with open(snippets_file, "r", encoding="utf-8") as f:
                snippets_data = json.load(f)
                # Get research goal from first company's data
                for domain, data in snippets_data.items():
                    if "research_goal" in data:
                        research_goal = data["research_goal"]
                        break
        except Exception as e:
            print(f"⚠️ Could not load research goal from debug data: {e}")
    
    state = GTMState(
        research_goal=research_goal,
        extracted_companies=companies,
        search_results=search_results,
        search_results_website=search_results_website,
        max_parallel_searches=5,
        confidence_threshold=0.8
    )
    
    return state

def test_evaluator_agent_only():
    """Test only the evaluator_agent"""
    
    print("🧪 Testing Evaluator Agent Only...")
    
    # Check if saved state exists
    if os.path.exists("test_state.json"):
        print("📁 Found existing test state, loading...")
        state = load_state("test_state.json")
        if not state:
            print("❌ Failed to load state, creating new one...")
            state = create_test_state()
    else:
        print("📝 Creating new test state from debug data...")
        state = create_test_state()
    
    print(f"🎯 Research Goal: {state.research_goal}")
    print(f"📋 Companies: {[c.domain for c in state.extracted_companies]}")
    
    # Show available evidence
    if state.search_results:
        print(f"📊 Search Results: {len(state.search_results)} companies")
    if state.search_results_website:
        print(f"🌐 Website Results: {len(state.search_results_website)} companies")
    
    try:
        # Run only the evaluator agent
        print("\n🚀 Running evaluator_agent...")
        result_state = evaluator_agent(state)
        
        print("\n✅ Evaluator Agent completed!")
        
        # Save the result state
        save_state(result_state, "test_state_after_evaluator.json")
        
        # Display results
        if result_state.final_findings:
            print("\n🎯 Evaluation Results:")
            for finding in result_state.final_findings:
                print(f"\n📌 {finding.domain}:")
                print(f"  Confidence Score: {finding.confidence_score}")
                print(f"  Evidence Sources: {finding.evidence_sources}")
                print(f"  Signals Found: {finding.signals_found}")
                print(f"  Uses AI for Fraud Detection: {finding.findings.get('ai_fraud_detection', 'N/A')}")
                print(f"  Technologies: {finding.findings.get('technologies', [])}")
                print(f"  Evidence Snippets: {len(finding.findings.get('evidence', []))}")
        else:
            print("❌ No evaluation results")
            
    except Exception as e:
        print(f"❌ Error testing evaluator agent: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function with command line options"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "save":
            # Save current state
            state = create_test_state()
            save_state(state)
            
        elif command == "load":
            # Load and display state
            state = load_state()
            if state:
                print(f"Research Goal: {state.research_goal}")
                print(f"Companies: {[c.domain for c in state.extracted_companies]}")
                if state.search_results:
                    print(f"Search Results: {list(state.search_results.keys())}")
                if state.search_results_website:
                    print(f"Website Results: {list(state.search_results_website.keys())}")
                
        elif command == "run":
            # Run the agent
            test_evaluator_agent_only()
            
        elif command == "clean":
            # Clean up test files
            files_to_remove = ["test_state.json", "test_state_after_evaluator.json"]
            for file in files_to_remove:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"🗑️ Removed {file}")
            print("✅ Cleaned up test files")
            
        else:
            print("Usage:")
            print("  python test_evaluator_agent.py save    - Save test state")
            print("  python test_evaluator_agent.py load    - Load and display state")
            print("  python test_evaluator_agent.py run     - Run evaluator agent")
            print("  python test_evaluator_agent.py clean   - Clean up test files")
            print("  python test_evaluator_agent.py         - Run evaluator agent (default)")
    else:
        # Default: run the agent
        test_evaluator_agent_only()

if __name__ == "__main__":
    main() 