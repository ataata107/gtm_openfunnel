from graph.gtm_graph import build_gtm_graph
from graph.state import GTMState

def main():
    """Main function to run the GTM research pipeline"""
    
    # Initialize the graph
    graph = build_gtm_graph()
    
    # Create initial state with different search depths for testing
    initial_state = GTMState(
        research_goal="Find fintech companies using AI for fraud detection",
        search_depth="quick",  # Try: "quick", "standard", "comprehensive"
        max_parallel_searches=100,
        confidence_threshold=0.8,
        max_iterations=1
    )
    
    print(f"🎯 Starting GTM Research Pipeline")
    print(f"📋 Research Goal: {initial_state.research_goal}")
    print(f"🔍 Search Depth: {initial_state.search_depth}")
    print(f"⚡ Max Parallel Searches: {initial_state.max_parallel_searches}")
    print(f"🎯 Confidence Threshold: {initial_state.confidence_threshold}")
    print("=" * 60)
    
    # Run the graph
    result = graph.invoke(initial_state)
    
    print("\n" + "=" * 60)
    print("✅ Research Pipeline Completed!")
    
    # Handle both dict and GTMState objects
    if isinstance(result, dict):
        extracted_companies = result.get("extracted_companies", [])
        final_findings = result.get("final_findings", [])
        quality_metrics = result.get("quality_metrics", {})
    else:
        extracted_companies = getattr(result, "extracted_companies", [])
        final_findings = getattr(result, "final_findings", [])
        quality_metrics = getattr(result, "quality_metrics", {})
    
    print(f"📊 Total Companies Found: {len(extracted_companies) if extracted_companies else 0}")
    print(f"📊 Final Findings: {len(final_findings) if final_findings else 0}")
    print(f"📊 Quality Score: {quality_metrics.get('quality_score', 0):.2f}" if quality_metrics else "N/A")
    print(f"📊 Coverage Score: {quality_metrics.get('coverage_score', 0):.2f}" if quality_metrics else "N/A")

if __name__ == "__main__":
    main()
