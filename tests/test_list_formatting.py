#!/usr/bin/env python3
"""
Test for list formatting in LLM prompts
"""

def test_list_formatting():
    """Test that lists are properly formatted for LLM prompts"""
    
    print("🧪 Testing List Formatting for LLM Prompts")
    print("=" * 50)
    
    # Sample data
    missing_aspects = [
        "Detailed case studies or examples of AI implementation",
        "Specific AI algorithms or models used",
        "Effectiveness or performance metrics of AI systems"
    ]
    
    coverage_gaps = [
        "Limited examples of successful AI applications",
        "Lack of diversity in company types analyzed",
        "Insufficient exploration of various AI technologies"
    ]
    
    evidence_issues = [
        "Some evidence snippets are outdated or lack specific dates",
        "Limited diversity in evidence sources, affecting reliability",
        "Vague evidence snippets that do not directly address the goal"
    ]
    
    recommendations = [
        "Conduct deeper research into specific AI technologies",
        "Seek out case studies or success stories",
        "Expand the analysis to include a wider range of companies"
    ]
    
    # Test the formatting logic
    def format_list_for_prompt(items, item_type="item"):
        """Format a list for LLM prompt consumption"""
        if not items:
            return f"No {item_type}s identified"
        return "\n".join([f"- {item}" for item in items])
    
    # Format the lists
    missing_aspects_text = format_list_for_prompt(missing_aspects, "missing aspect")
    coverage_gaps_text = format_list_for_prompt(coverage_gaps, "coverage gap")
    evidence_issues_text = format_list_for_prompt(evidence_issues, "evidence issue")
    recommendations_text = format_list_for_prompt(recommendations, "recommendation")
    
    print("\n📋 Original Lists (Python format):")
    print(f"Missing Aspects: {missing_aspects}")
    print(f"Coverage Gaps: {coverage_gaps}")
    print(f"Evidence Issues: {evidence_issues}")
    print(f"Recommendations: {recommendations}")
    
    print("\n✅ Formatted Lists (LLM-friendly format):")
    print(f"Missing Aspects:\n{missing_aspects_text}")
    print(f"\nCoverage Gaps:\n{coverage_gaps_text}")
    print(f"\nEvidence Issues:\n{evidence_issues_text}")
    print(f"\nRecommendations:\n{recommendations_text}")
    
    # Test edge cases
    print("\n🔍 Testing Edge Cases:")
    
    # Empty list
    empty_list = []
    empty_text = format_list_for_prompt(empty_list, "item")
    print(f"Empty list: '{empty_text}'")
    
    # Single item
    single_item = ["Only one item"]
    single_text = format_list_for_prompt(single_item, "item")
    print(f"Single item: {single_text}")
    
    # Long items
    long_items = [
        "This is a very long item that might cause formatting issues in the prompt",
        "Another long item with lots of details and specific information"
    ]
    long_text = format_list_for_prompt(long_items, "item")
    print(f"Long items:\n{long_text}")
    
    print("\n✅ List formatting test completed!")
    print("💡 Lists should now be properly formatted for LLM consumption")

def test_company_analysis_formatting():
    """Test company analysis formatting"""
    
    print("\n🧪 Testing Company Analysis Formatting")
    print("=" * 50)
    
    # Mock company analysis data
    company_analyses = [
        {
            "company_domain": "stripe.com",
            "quality_score": 0.90,
            "coverage_score": 0.85,
            "gaps": [
                "Lack of detailed case studies",
                "No information on specific algorithms",
                "Absence of user testimonials"
            ],
            "evidence_issues": [
                "Some evidence lacks citations",
                "Evidence may not be recent enough"
            ]
        },
        {
            "company_domain": "square.com",
            "quality_score": 0.70,
            "coverage_score": 0.50,
            "gaps": [
                "Lack of specific examples",
                "No mention of AI algorithms"
            ],
            "evidence_issues": [
                "Vague evidence snippets",
                "Outdated information"
            ]
        }
    ]
    
    # Format company analyses
    company_analyses_text = ""
    for analysis in company_analyses:
        gaps = analysis.get('gaps', [])
        gaps_text = "\n".join([f"  * {gap}" for gap in gaps[:3]]) if gaps else "None identified"
        
        issues = analysis.get('evidence_issues', [])
        issues_text = "\n".join([f"  * {issue}" for issue in issues[:3]]) if issues else "None identified"
        
        company_analyses_text += f"""
        Company: {analysis.get('company_domain', 'N/A')}
        Quality: {analysis.get('quality_score', 0):.2f}
        Coverage: {analysis.get('coverage_score', 0):.2f}
        Gaps:
        {gaps_text}
        Issues:
        {issues_text}
        """
    
    print("✅ Formatted Company Analysis:")
    print(company_analyses_text)
    
    print("\n✅ Company analysis formatting test completed!")

if __name__ == "__main__":
    test_list_formatting()
    test_company_analysis_formatting()
    
    print("\n🎉 All formatting tests completed!")
    print("💡 Lists are now properly formatted for LLM consumption") 