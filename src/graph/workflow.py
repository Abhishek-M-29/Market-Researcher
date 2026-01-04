"""
LangGraph Workflow: The Recursive State Machine

This module defines the complete graph topology for the market research engine.
It implements the flow defined in the blueprint:

1. START -> Strategist -> Critic
2. CONDITION: If not verified, loop back to Strategist
3. Infiltrator -> Anthropologist -> Analyzer
4. Innovator -> Auditor
5. CONDITION: If not viable, loop back to Innovator
6. PDF_Compiler -> END
"""

from typing import Literal
from langgraph.graph import StateGraph, END

from src.graph.state import MarketState
from src.agents import (
    run_strategist,
    run_critic,
    run_infiltrator,
    run_anthropologist,
    run_analyzer,
    run_innovator,
    run_auditor,
    run_pdf_compiler
)


def create_initial_state(raw_idea: str, target_region: str = "India") -> MarketState:
    """
    Create the initial state for a new research run.
    """
    return {
        # Inputs
        "raw_idea": raw_idea,
        "target_region": target_region,
        
        # Research Data
        "raw_pains": [],
        "verified_pains": [],
        "problem_statement": "",
        "delta_4_logic": "",
        
        # Competitive Intelligence
        "competitor_table": [],
        
        # Personas
        "personas": [],
        
        # Features
        "feature_list": [],
        
        # Financials
        "business_model": {},
        "revenue_model": {},
        
        # Control Flags
        "is_verified": False,
        "is_financially_viable": False,
        "iteration_count": 0,
        "max_iterations": 3,
        
        # Feedback
        "critic_feedback": None,
        "auditor_feedback": None,
        
        # Output
        "final_report_path": None
    }


def should_loop_to_strategist(state: MarketState) -> Literal["strategist", "infiltrator"]:
    """
    Conditional edge: After Critic, should we loop back to Strategist?
    
    Returns:
        "strategist" if more research needed
        "infiltrator" if verified and ready to proceed
    """
    is_verified = state.get("is_verified", False)
    iteration = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 3)
    
    if not is_verified and iteration < max_iterations:
        return "strategist"
    else:
        return "infiltrator"


def should_loop_to_innovator(state: MarketState) -> Literal["innovator", "pdf_compiler"]:
    """
    Conditional edge: After Auditor, should we loop back to Innovator?
    
    Returns:
        "innovator" if financials need refinement
        "pdf_compiler" if viable and ready for final report
    """
    is_viable = state.get("is_financially_viable", False)
    iteration = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 3)
    
    # Allow up to 2 viability loops (use different counter or just proceed after verification loops)
    if not is_viable and iteration < max_iterations + 2:
        return "innovator"
    else:
        return "pdf_compiler"


def build_graph() -> StateGraph:
    """
    Build and return the complete research workflow graph.
    """
    # Create the graph with our state schema
    workflow = StateGraph(MarketState)
    
    # Add all nodes (agents)
    workflow.add_node("strategist", run_strategist)
    workflow.add_node("critic", run_critic)
    workflow.add_node("infiltrator", run_infiltrator)
    workflow.add_node("anthropologist", run_anthropologist)
    workflow.add_node("analyzer", run_analyzer)
    workflow.add_node("innovator", run_innovator)
    workflow.add_node("auditor", run_auditor)
    workflow.add_node("pdf_compiler", run_pdf_compiler)
    
    # Define the edges (flow)
    
    # Entry point
    workflow.set_entry_point("strategist")
    
    # Strategist -> Critic
    workflow.add_edge("strategist", "critic")
    
    # Critic -> (conditional) Strategist OR Infiltrator
    workflow.add_conditional_edges(
        "critic",
        should_loop_to_strategist,
        {
            "strategist": "strategist",
            "infiltrator": "infiltrator"
        }
    )
    
    # Infiltrator -> Anthropologist -> Analyzer -> Innovator
    workflow.add_edge("infiltrator", "anthropologist")
    workflow.add_edge("anthropologist", "analyzer")
    workflow.add_edge("analyzer", "innovator")
    
    # Innovator -> Auditor
    workflow.add_edge("innovator", "auditor")
    
    # Auditor -> (conditional) Innovator OR PDF_Compiler
    workflow.add_conditional_edges(
        "auditor",
        should_loop_to_innovator,
        {
            "innovator": "innovator",
            "pdf_compiler": "pdf_compiler"
        }
    )
    
    # PDF_Compiler -> END
    workflow.add_edge("pdf_compiler", END)
    
    return workflow


def compile_graph():
    """
    Build and compile the graph for execution.
    """
    workflow = build_graph()
    return workflow.compile()


# Create a runnable graph instance
def get_runnable_graph():
    """
    Get a compiled, runnable graph instance.
    """
    return compile_graph()
