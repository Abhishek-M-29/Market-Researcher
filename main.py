"""
Market Research Engine - CLI Entry Point

Run this to execute the full research pipeline from the command line.
For an interactive experience, use the Streamlit app (app.py).

Usage:
    python main.py "Your startup idea here"
    python main.py "Your startup idea here" --region "India"
"""

import sys
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.graph import get_runnable_graph, create_initial_state


def run_research(idea: str, region: str = "India") -> dict:
    """
    Execute the full market research pipeline.
    
    Args:
        idea: The startup idea to research
        region: Target geographic region (default: India)
    
    Returns:
        The final state containing all research results
    """
    print(f"\n{'='*60}")
    print(f"🚀 Starting Market Research for: {idea}")
    print(f"📍 Target Region: {region}")
    print(f"{'='*60}\n")
    
    # Create initial state
    initial_state = create_initial_state(idea, region)
    
    # Get the compiled graph
    graph = get_runnable_graph()
    
    # Run the graph with streaming to show progress
    print("📊 Running research pipeline...\n")
    
    current_node = None
    for event in graph.stream(initial_state):
        # Extract the node name and state update
        for node_name, state_update in event.items():
            if node_name != current_node:
                current_node = node_name
                print(f"✓ Completed: {node_name.replace('_', ' ').title()}")
    
    # Get final state
    final_state = graph.invoke(initial_state)
    
    print(f"\n{'='*60}")
    print("✅ Research Complete!")
    print(f"{'='*60}\n")
    
    # Print summary
    print("📋 Summary:")
    print(f"   - Verified Pain Points: {len(final_state.get('verified_pains', []))}")
    print(f"   - Competitors Analyzed: {len(final_state.get('competitor_table', []))}")
    print(f"   - Personas Created: {len(final_state.get('personas', []))}")
    print(f"   - Features Proposed: {len(final_state.get('feature_list', []))}")
    
    revenue_model = final_state.get('revenue_model', {})
    print(f"   - LTV/CAC Ratio: {revenue_model.get('ltv_cac_ratio', 'N/A')}")
    print(f"   - Financially Viable: {'✅ Yes' if final_state.get('is_financially_viable') else '❌ No'}")
    
    report_path = final_state.get('final_report_path')
    if report_path:
        print(f"\n📄 Report saved to: {report_path}")
    
    return final_state


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Agent Market Research Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py "AI-powered expense tracker for freelancers"
    python main.py "Hyperlocal grocery delivery" --region "India"
        """
    )
    
    parser.add_argument(
        "idea",
        type=str,
        help="The startup idea to research"
    )
    
    parser.add_argument(
        "--region",
        type=str,
        default="India",
        help="Target geographic region (default: India)"
    )
    
    args = parser.parse_args()
    
    # Run the research
    result = run_research(args.idea, args.region)
    
    return result


if __name__ == "__main__":
    main()
