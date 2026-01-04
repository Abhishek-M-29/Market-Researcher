"""
Financial Modeling Engine for the Auditor agent.

This module performs deterministic financial calculations instead of
relying on LLM estimations. The LLM's job is to estimate inputs;
this module does the math.

Key Formulas:
    LTV = (ARPU × Gross Margin) / Monthly Churn Rate
    Payback Period = CAC / (ARPU × Gross Margin)
    LTV/CAC Ratio = LTV / CAC (should be > 3 for viability)
"""

import pandas as pd
from typing import Dict, Any, Optional
from dataclasses import dataclass
from src.config.settings import MIN_LTV_CAC_RATIO


@dataclass
class FinancialInputs:
    """Input parameters for financial modeling."""
    cac: float                      # Customer Acquisition Cost (₹)
    arpu: float                     # Average Revenue Per User (₹/month)
    gross_margin: float             # As decimal (0.7 = 70%)
    monthly_churn_rate: float       # As decimal (0.05 = 5%)
    pricing_tiers: Dict[str, float] # Name -> Price mapping


@dataclass
class FinancialOutputs:
    """Calculated financial metrics."""
    ltv: float
    ltv_cac_ratio: float
    payback_months: float
    monthly_contribution: float     # ARPU × Gross Margin
    is_viable: bool
    viability_feedback: str


def calculate_ltv(arpu: float, gross_margin: float, churn_rate: float) -> float:
    """
    Calculate Customer Lifetime Value.
    
    Formula: LTV = (ARPU × Gross Margin) / Churn Rate
    
    Example:
        ARPU = ₹199/month
        Gross Margin = 70%
        Churn = 5%/month
        LTV = (199 × 0.7) / 0.05 = ₹2,786
    """
    if churn_rate <= 0:
        # If churn is 0, LTV is infinite (not realistic)
        return float('inf')
    
    return (arpu * gross_margin) / churn_rate


def calculate_payback_months(cac: float, arpu: float, gross_margin: float) -> float:
    """
    Calculate how many months to recover CAC.
    
    Formula: Payback = CAC / (ARPU × Gross Margin)
    
    Example:
        CAC = ₹500
        ARPU = ₹199
        Gross Margin = 70%
        Payback = 500 / (199 × 0.7) = 3.6 months
    """
    monthly_contribution = arpu * gross_margin
    
    if monthly_contribution <= 0:
        return float('inf')
    
    return cac / monthly_contribution


def analyze_financials(inputs: FinancialInputs) -> FinancialOutputs:
    """
    Perform complete financial analysis and viability check.
    
    This is the main function called by the Auditor agent.
    """
    # Calculate core metrics
    ltv = calculate_ltv(
        inputs.arpu,
        inputs.gross_margin,
        inputs.monthly_churn_rate
    )
    
    payback = calculate_payback_months(
        inputs.cac,
        inputs.arpu,
        inputs.gross_margin
    )
    
    monthly_contribution = inputs.arpu * inputs.gross_margin
    
    # Calculate the magic ratio
    ltv_cac_ratio = ltv / inputs.cac if inputs.cac > 0 else float('inf')
    
    # Determine viability
    is_viable = ltv_cac_ratio >= MIN_LTV_CAC_RATIO
    
    # Generate feedback
    if is_viable:
        feedback = (
            f"✅ Financially viable. LTV/CAC ratio of {ltv_cac_ratio:.2f} "
            f"exceeds the minimum threshold of {MIN_LTV_CAC_RATIO}."
        )
    else:
        gap = MIN_LTV_CAC_RATIO - ltv_cac_ratio
        feedback = generate_improvement_suggestions(inputs, ltv_cac_ratio, gap)
    
    return FinancialOutputs(
        ltv=round(ltv, 2),
        ltv_cac_ratio=round(ltv_cac_ratio, 2),
        payback_months=round(payback, 2),
        monthly_contribution=round(monthly_contribution, 2),
        is_viable=is_viable,
        viability_feedback=feedback
    )


def generate_improvement_suggestions(
    inputs: FinancialInputs,
    current_ratio: float,
    gap: float
) -> str:
    """
    Generate specific suggestions to improve financial viability.
    """
    suggestions = [
        f"❌ Not viable. LTV/CAC ratio of {current_ratio:.2f} "
        f"is below the minimum threshold of {MIN_LTV_CAC_RATIO}.\n",
        "Suggestions to improve viability:\n"
    ]
    
    # Suggestion 1: Reduce CAC
    target_cac = inputs.arpu * inputs.gross_margin / inputs.monthly_churn_rate / MIN_LTV_CAC_RATIO
    if target_cac < inputs.cac:
        suggestions.append(
            f"1. Reduce CAC from ₹{inputs.cac:.0f} to ₹{target_cac:.0f} "
            f"(focus on organic growth, referrals, or cheaper channels)"
        )
    
    # Suggestion 2: Increase ARPU
    current_ltv = inputs.arpu * inputs.gross_margin / inputs.monthly_churn_rate
    target_ltv = inputs.cac * MIN_LTV_CAC_RATIO
    target_arpu = (target_ltv * inputs.monthly_churn_rate) / inputs.gross_margin
    if target_arpu > inputs.arpu:
        suggestions.append(
            f"2. Increase ARPU from ₹{inputs.arpu:.0f} to ₹{target_arpu:.0f} "
            f"(add premium tiers, upsells, or usage-based pricing)"
        )
    
    # Suggestion 3: Reduce churn
    target_churn = (inputs.arpu * inputs.gross_margin) / (inputs.cac * MIN_LTV_CAC_RATIO)
    if target_churn < inputs.monthly_churn_rate:
        suggestions.append(
            f"3. Reduce monthly churn from {inputs.monthly_churn_rate*100:.1f}% "
            f"to {target_churn*100:.1f}% (improve onboarding, add stickiness features)"
        )
    
    return "\n".join(suggestions)


def generate_projection_table(
    inputs: FinancialInputs,
    months: int = 24,
    initial_customers: int = 100,
    monthly_growth_rate: float = 0.1
) -> pd.DataFrame:
    """
    Generate a month-by-month P&L projection.
    
    This creates a DataFrame that can be used for visualization
    or exported to the final report.
    """
    data = []
    customers = initial_customers
    cumulative_revenue = 0
    cumulative_cost = 0
    
    for month in range(1, months + 1):
        # Calculate new customers this month
        new_customers = int(customers * monthly_growth_rate)
        
        # Calculate churned customers
        churned = int(customers * inputs.monthly_churn_rate)
        
        # Update customer count
        customers = customers - churned + new_customers
        
        # Calculate financials
        revenue = customers * inputs.arpu
        cogs = revenue * (1 - inputs.gross_margin)
        gross_profit = revenue - cogs
        cac_spend = new_customers * inputs.cac
        net = gross_profit - cac_spend
        
        cumulative_revenue += revenue
        cumulative_cost += (cogs + cac_spend)
        
        data.append({
            'Month': month,
            'Customers': customers,
            'New Customers': new_customers,
            'Churned': churned,
            'Revenue (₹)': round(revenue, 2),
            'Gross Profit (₹)': round(gross_profit, 2),
            'CAC Spend (₹)': round(cac_spend, 2),
            'Net (₹)': round(net, 2),
            'Cumulative Revenue (₹)': round(cumulative_revenue, 2),
            'Cumulative Profit (₹)': round(cumulative_revenue - cumulative_cost, 2),
        })
    
    return pd.DataFrame(data)


def dict_to_inputs(data: Dict[str, Any]) -> FinancialInputs:
    """
    Convert a dictionary (from LLM output) to FinancialInputs.
    """
    return FinancialInputs(
        cac=float(data.get('cac', 0)),
        arpu=float(data.get('arpu', 0)),
        gross_margin=float(data.get('gross_margin', 0.7)),
        monthly_churn_rate=float(data.get('churn_rate', 0.05)),
        pricing_tiers=data.get('pricing_tiers', {})
    )
