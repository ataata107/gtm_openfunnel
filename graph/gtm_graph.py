from langgraph.graph import StateGraph, END
from graph.state import GTMState
from agents.query_agent import query_agent
from agents.company_aggregator_agent import company_aggregator_agent
from agents.multi_source_search_agent import multi_source_search_agent
from agents.website_scraper_agent import website_scraper_agent  # ✅ New
from agents.quality_evaluator_agent import quality_evaluator_agent
from agents.strategy_refinement_agent import strategy_refinement_agent

def build_gtm_graph():
    builder = StateGraph(GTMState)

    # Add agent nodes
    builder.add_node("QueryAgent", query_agent)
    builder.add_node("CompanyAggregatorAgent", company_aggregator_agent)
    builder.add_node("SearchAgent", multi_source_search_agent)
    builder.add_node("WebsiteScraperAgent", website_scraper_agent)  # ✅ Added
    builder.add_node("QualityEvaluatorAgent", quality_evaluator_agent)
    builder.add_node("StrategyRefinementAgent", strategy_refinement_agent)

    # Entry point
    builder.set_entry_point("QueryAgent")

    # ✅ Sequential execution: Linear flow
    builder.set_entry_point("QueryAgent")
    builder.add_edge("QueryAgent", "CompanyAggregatorAgent")
    builder.add_edge("CompanyAggregatorAgent", "SearchAgent")
    # builder.add_edge("SearchAgent", "WebsiteScraperAgent")
    builder.add_edge("SearchAgent", "QualityEvaluatorAgent")

    # Feedback loop: If quality is low, loop back to search with refined strategies
    def should_continue_research(state):
        """Determine if we should continue research based on quality metrics and iteration count"""
        quality_metrics = state.quality_metrics or {}
        coverage_score = quality_metrics.get('coverage_score', 0)
        quality_score = quality_metrics.get('quality_score', 0)
        
        # Check iteration limits
        if state.iteration_count >= state.max_iterations:
            print(f"🛑 Reached maximum iterations ({state.max_iterations}). Stopping research.")
            return False
        
        # Continue if either coverage or quality is below threshold
        should_continue = coverage_score < 0.8 or quality_score < 0.7
        
        if should_continue:
            print(f"🔄 Quality below threshold (Coverage: {coverage_score:.2f}, Quality: {quality_score:.2f}). Continuing research...")
        else:
            print(f"✅ Quality threshold met (Coverage: {coverage_score:.2f}, Quality: {quality_score:.2f}). Stopping research.")
        
        return should_continue
    
    # Conditional edge: QualityEvaluatorAgent -> QueryAgent (if quality is low)
    builder.add_conditional_edges(
        "QualityEvaluatorAgent",
        should_continue_research,
        {
            True: "QueryAgent",  # Loop back to query agent to generate new strategies
            False: "__end__"      # End if quality is good enough
        }
    )

    # Compile and visualize
    compiled_graph = builder.compile()

    try:
        graph_image = compiled_graph.get_graph().draw_mermaid_png()
        with open("gtm_graph.png", "wb") as f:
            f.write(graph_image)
        print("📊 Graph saved as gtm_graph.png")
    except Exception as e:
        print(f"⚠️ Could not save graph image: {e}")

    return compiled_graph

if __name__ == "__main__":
    print("🔗 Building GTM Graph...")
    graph = build_gtm_graph()
    print("✅ Graph built successfully!")
    print(f"Graph nodes: {list(graph.nodes.keys())}")
    print(f"Entry point: {graph.entry_point}")
