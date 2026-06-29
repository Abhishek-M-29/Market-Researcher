"""
Financial Calculation Tools.

Deterministic financial models that agents can call without LLM overhead.
"""

from typing import Dict, Any
from langchain_core.tools import tool
from src.utils.financials import calculate_ltv, calculate_payback, FinancialInputs, analyze_financials


@tool
def calculate_unit_economics(
    cac: float,
    arpu: float,
    gross_margin: float,
    churn_rate: float
) -> Dict[str, Any]:
    """
    Calculate unit economics metrics (LTV, LTV/CAC ratio, payback period) for a business model.
    
    Args:
        cac: Customer Acquisition Cost in ₹
        arpu: Average Revenue Per User per month in ₹
        gross_margin: Gross margin as decimal (e.g., 0.7 for 70%)
        churn_rate: Monthly churn rate as decimal (e.g., 0.05 for 5%)
    
    Returns:
        Dictionary with ltv, ltv_cac_ratio, payback_months, and viability assessment.
    """
    try:
        ltv = calculate_ltv(arpu, gross_margin, churn_rate)
        ltv_cac_ratio = ltv / cac if cac > 0 else 0
        payback_months = calculate_payback(cac, arpu, gross_margin)
        
        # Viability thresholds
        is_viable = ltv_cac_ratio >= 3.0 and payback_months <= 12
        
        return {
            "ltv": round(ltv, 2),
            "ltv_cac_ratio": round(ltv_cac_ratio, 2),
            "payback_months": round(payback_months, 1),
            "is_financially_viable": is_viable,
            "assessment": "Viable" if is_viable else "Needs improvement",
            "recommendation": (
                "Strong unit economics" if ltv_cac_ratio >= 3.0 
                else f"Improve LTV/CAC ratio (current: {ltv_cac_ratio:.2f}, target: 3.0+)"
            )
        }
    except Exception as e:
        return {
            "error": str(e),
            "is_financially_viable": False
        }


@tool
def run_financial_model(
    cac: float,
    arpu: float,
    gross_margin: float,
    churn_rate: float,
    pricing_tiers: Dict[str, float]
) -> Dict[str, Any]:
    """
    Run a complete financial analysis with projections and viability assessment.
    
    Args:
        cac: Customer Acquisition Cost in ₹
        arpu: Average Revenue Per User per month in ₹
        gross_margin: Gross margin as decimal (0.7 = 70%)
        churn_rate: Monthly churn rate as decimal (0.05 = 5%)
        pricing_tiers: Dictionary of pricing tiers (e.g., {"Basic": 99, "Pro": 299})
    
    Returns:
        Complete financial model with projections, metrics, and recommendations.
    """
    try:
        inputs = FinancialInputs(
            cac=cac,
            arpu=arpu,
            gross_margin=gross_margin,
            churn_rate=churn_rate
        )
        
        results = analyze_financials(inputs)
        results["pricing_tiers"] = pricing_tiers
        
        return results
    except Exception as e:
        return {
            "error": str(e),
            "is_financially_viable": False
        }
