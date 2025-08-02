from graph.gtm_graph import build_gtm_graph
from graph.state import GTMState

if __name__ == "__main__":
    gtm_workflow = build_gtm_graph()

    sample_state = GTMState(
        research_goal="Find fintech companies using AI for fraud detection",
        search_depth="comprehensive",
        max_parallel_searches=100,
        confidence_threshold=0.8,
        max_iterations=2
    )

    final_state = gtm_workflow.invoke(sample_state)

    # print("\n✅ Final Queries:\n")

    # Handle both dict and GTMState objects
    if isinstance(final_state, dict):
        queries = final_state.get("search_strategies_generated", [])
        companies = final_state.get("extracted_companies", [])
        search_results_serper = final_state.get("search_results_serper", {})
        search_results_website = final_state.get("search_results_website", {})
        findings = final_state.get("final_findings", [])
    else:
        queries = getattr(final_state, "search_strategies_generated", [])
        companies = getattr(final_state, "extracted_companies", [])
        search_results_serper = getattr(final_state, "search_results_serper", {})
        search_results_website = getattr(final_state, "search_results_website", {})
        findings = getattr(final_state, "final_findings", [])

    # # Display generated queries
    # if queries:
    #     for q in queries:
    #         print("-", q)
    # else:
    #     print("❌ No queries generated.")
    #     print("Final state:", final_state)

    # Display extracted companies
    # if companies:
    #     print("\n🏢 Extracted Companies:")
    #     for c in companies:
    #         print(f"- {c.name} ({c.domain}) — Source: {c.source_url}")
    # else:
    #     print("\n⚠️ No companies extracted.")

    # Display serper search results
    # if search_results_serper:
    #     print("\n🔍 Serper Search Results:")
    #     for domain, snippets in search_results_serper.items():
    #         print(f"\nDomain: {domain}")
    #         for i, snippet in enumerate(snippets):
    #             print(f"  {i+1}. {snippet[:100]}...")
    # else:
    #     print("\n📝 No serper search results found.")

    # Display website search results
    # if search_results_website:
    #     print("\n🌐 Website Search Results:")
    #     for domain, snippets in search_results_website.items():
    #         print(f"\nDomain: {domain}")
    #         for i, snippet in enumerate(snippets):
    #             print(f"  {i+1}. {snippet[:100]}...")
    # else:
    #     print("\n📝 No website search results found.")

    # Display evaluator output with new structure
    # if findings:
    #     print("\n🧠 Evaluated Findings:")
    #     for f in findings:
    #         print(f"\n📌 {f.domain}")
    #         print(f"  Confidence Score: {f.confidence_score}")
    #         print(f"  Goal Achieved: {f.findings.get('goal_achieved', 'N/A')}")
    #         print(f"  Confidence Level: {f.findings.get('confidence_level', 'N/A')}")
    #         print(f"  Technologies: {f.findings.get('technologies', [])}")
    #         print(f"  Evidence Sources: {f.evidence_sources}")
    #         print(f"  Signals Found: {f.signals_found}")
    #         print("  Evidence Snippets:")
    #         for ev in f.findings.get("evidences", []):
    #             print(f"   - {ev[:100]}...")
            
    #         # Show research goal for context
    #         research_goal = f.findings.get("research_goal", "Unknown")
    #         print(f"  Research Goal: {research_goal}")
    # else:
    #     print("\n⚠️ No evaluated findings.")

    # print(f"\n🎯 Research Goal: {sample_state.research_goal}")
    # print(f"📊 Total Companies Evaluated: {len(findings) if findings else 0}")
