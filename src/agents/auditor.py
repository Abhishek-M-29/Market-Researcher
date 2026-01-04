"""
Agent 7: The Auditor

Role: Validate financial viability with unit economics.
Uses: Pandas Financial Modeling Engine + LLM for estimation

The Auditor:
1. Gets pricing/cost assumptions from LLM
2. Runs them through our deterministic financial model
3. Either approves (is_financially_viable=True) or rejects with specific suggestions
"""

import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from src.graph.state import MarketState
from src.config.prompts import AUDITOR_PROMPT
from src.utils.llm import get_analysis_llm
from src.utils.financials import (
    analyze_financials,
    dict_to_inputs,
    generate_projection_table,
    FinancialInputs
)


def run_auditor(state: MarketState) -> Dict[str, Any]:
    """
    Execute the Auditor agent.
    
    Inputs from state:
        - feature_list: Features to cost
        - personas: Target users for pricing
        - competitor_table: Competitive pricing context
    
    Outputs to state:
        - revenue_model: Calculated financials
        - business_model: Business model canvas
        - is_financially_viable: Pass/fail
        - auditor_feedback: If failed, what to change
    """
    idea = state.get("raw_idea", "")
    features = state.get("feature_list", [])
    personas = state.get("personas", [])
    competitors = state.get("competitor_table", [])
    iteration = state.get("iteration_count", 0)
    
    # Extract competitive pricing context
    competitor_pricing = []
    for c in competitors:
        pricing = c.get("scraped_pricing", {}) or c.get("pricing_tiers", {})
        if pricing:
            competitor_pricing.append({
                "name": c.get("name", "Unknown"),
                "pricing": pricing
            })
    
    # Calculate total effort from features
    total_effort_weeks = sum(f.get("effort", 0) for f in features[:10])  # Top 10 features
    
    # Persona income context for pricing
    persona_incomes = [
        f"- {p.get('name', '')}: {p.get('income_bracket', 'Unknown')}"
        for p in personas[:5]
    ]
    
    llm = get_analysis_llm()
    
    messages = [
        SystemMessage(content=AUDITOR_PROMPT),
        HumanMessage(content=f"""
IDEA: {idea}

TOP 10 FEATURES (by RICE score):
{json.dumps([{"name": f.get("name"), "effort_weeks": f.get("effort")} for f in features[:10]], indent=2)}

TOTAL DEVELOPMENT EFFORT: {total_effort_weeks} person-weeks

COMPETITIVE PRICING:
{json.dumps(competitor_pricing, indent=2)}

TARGET PERSONA INCOMES:
{chr(10).join(persona_incomes)}

Based on this context, estimate realistic values for:
1. CAC (Customer Acquisition Cost) - Consider Indian digital marketing costs
2. ARPU (Average Revenue Per User per month) - Based on competitive pricing and persona incomes
3. Gross Margin (as decimal, e.g., 0.7 for 70%)
4. Monthly Churn Rate (as decimal, e.g., 0.05 for 5%)
5. Pricing Tiers

Also define the business model:
- Key Partners
- Cost Structure
- Revenue Streams

Return your response as valid JSON matching the output format specified.
""")
    ]
    
    response = llm.invoke(messages)
    
    # Parse LLM response
    try:
        content = response.content
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            parsed = json.loads(content[json_start:json_end])
            llm_financials = parsed.get("financials", {})
            business_model = parsed.get("business_model", {})
        else:
            llm_financials = {}
            business_model = {}
    except json.JSONDecodeError:
        llm_financials = {}
        business_model = {}
    
    # Use default values if LLM didn't provide
    financial_inputs = FinancialInputs(
        cac=float(llm_financials.get("cac", 500)),
        arpu=float(llm_financials.get("arpu", 199)),
        gross_margin=float(llm_financials.get("gross_margin", 0.7)),
        monthly_churn_rate=float(llm_financials.get("churn_rate", 0.05)),
        pricing_tiers=llm_financials.get("pricing_tiers", {"Basic": 99, "Pro": 299})
    )
    
    # Run our deterministic financial analysis
    financial_results = analyze_financials(financial_inputs)
    
    # Generate 24-month projection
    projection = generate_projection_table(financial_inputs)
    
    # Build revenue model for state
    revenue_model = {
        "cac": financial_inputs.cac,
        "arpu": financial_inputs.arpu,
        "gross_margin": financial_inputs.gross_margin,
        "churn_rate": financial_inputs.monthly_churn_rate,
        "ltv": financial_results.ltv,
        "ltv_cac_ratio": financial_results.ltv_cac_ratio,
        "payback_months": financial_results.payback_months,
        "pricing_tiers": financial_inputs.pricing_tiers,
        "viability_ratio": financial_results.ltv_cac_ratio
    }
    
    # Determine viability
    is_viable = financial_results.is_viable
    
    # Generate feedback if not viable
    if not is_viable:
        feedback = financial_results.viability_feedback
    else:
        feedback = ""
    
    return {
        "revenue_model": revenue_model,
        "business_model": business_model,
        "is_financially_viable": is_viable,
        "auditor_feedback": feedback,
        "financial_projection": projection.to_dict('records')[:6],  # First 6 months
        "monthly_contribution": financial_results.monthly_contribution
    }


def should_loop_to_innovator(state: MarketState) -> bool:
    """
    Conditional edge function: Should we loop back to Innovator?
    
    Returns True if:
    - Not financially viable AND
    - Haven't exceeded max viability loops (2)
    """
    is_viable = state.get("is_financially_viable", False)
    iteration = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 3)
    
    # Allow up to 2 viability refinement loops
    return not is_viable and iteration < max_iterations
