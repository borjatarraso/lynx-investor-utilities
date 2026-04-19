"""Metric relevance by company tier AND energy development stage.

Defines which metrics are CRITICAL, RELEVANT, CONTEXTUAL, or IRRELEVANT
for each combination of company size tier and development stage.

For energy sector analysis:
  CRITICAL    — Must-check metric for this stage. Highlighted with bold star marker.
                E.g. cash_runway for explorers, EV/EBITDA for producers.
  RELEVANT    — Important and displayed normally. Useful context for the analysis.
  CONTEXTUAL  — Shown dimmed. Informational only, not a primary decision driver.
  IRRELEVANT  — Not meaningful for this stage/tier. Hidden or struck-through.

The relevance system drives visual highlighting across all four interface modes
(console, interactive, TUI, GUI) to guide investors toward the metrics that
matter most for energy companies at each development stage.
"""

from __future__ import annotations

from lynx_energy.models import CompanyStage, CompanyTier, Relevance

C = Relevance.CRITICAL
M = Relevance.IMPORTANT
R = Relevance.RELEVANT
X = Relevance.CONTEXTUAL
I = Relevance.IRRELEVANT


def get_relevance(
    metric_key: str,
    tier: CompanyTier,
    category: str = "valuation",
    stage: CompanyStage = CompanyStage.EXPLORER,
) -> Relevance:
    """Look up relevance for a metric given tier and stage.

    Stage overrides take precedence over tier-based lookups because
    the development stage is the primary axis for energy analysis.
    """
    stage_override = _STAGE_OVERRIDES.get(metric_key, {}).get(stage)
    if stage_override is not None:
        return stage_override

    table = {
        "valuation": VALUATION_RELEVANCE,
        "profitability": PROFITABILITY_RELEVANCE,
        "solvency": SOLVENCY_RELEVANCE,
        "growth": GROWTH_RELEVANCE,
        "energy_quality": ENERGY_QUALITY_RELEVANCE,
        "share_structure": SHARE_STRUCTURE_RELEVANCE,
    }.get(category, {})
    entry = table.get(metric_key, {})
    return entry.get(tier, Relevance.RELEVANT)


# ======================================================================
# Stage-based overrides (take precedence over tier-based lookups)
# ======================================================================

_STAGE_OVERRIDES: dict[str, dict[CompanyStage, Relevance]] = {
    # VALUATION
    "pe_trailing": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: M, CompanyStage.ROYALTY: M},
    "pe_forward": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: X, CompanyStage.ROYALTY: R},
    "p_fcf": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: C, CompanyStage.ROYALTY: C},
    "ev_ebitda": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: X, CompanyStage.PRODUCER: C, CompanyStage.ROYALTY: C},
    "ev_revenue": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: X, CompanyStage.PRODUCER: M, CompanyStage.ROYALTY: M},
    "peg_ratio": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: X, CompanyStage.ROYALTY: X},
    "dividend_yield": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: X, CompanyStage.ROYALTY: R},
    "earnings_yield": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    "cash_to_market_cap": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: M, CompanyStage.PRODUCER: X, CompanyStage.ROYALTY: X},
    "pb_ratio": {CompanyStage.GRASSROOTS: R, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: C, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    "price_to_tangible_book": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: C, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: X},
    "price_to_ncav": {CompanyStage.GRASSROOTS: R, CompanyStage.EXPLORER: R, CompanyStage.DEVELOPER: X, CompanyStage.PRODUCER: X, CompanyStage.ROYALTY: I},
    "ps_ratio": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    "fcf_yield": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: C, CompanyStage.ROYALTY: C},
    # PROFITABILITY
    "roe": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: M, CompanyStage.ROYALTY: C},
    "roa": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    "roic": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: C, CompanyStage.ROYALTY: C},
    "gross_margin": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: C, CompanyStage.ROYALTY: R},
    "operating_margin": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    "net_margin": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    "fcf_margin": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: C, CompanyStage.ROYALTY: C},
    "ebitda_margin": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    "croci": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: C, CompanyStage.ROYALTY: R},
    "ocf_to_net_income": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    # SOLVENCY
    "cash_burn_rate": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: C, CompanyStage.PRODUCER: X, CompanyStage.ROYALTY: I},
    "cash_runway_years": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: C, CompanyStage.PRODUCER: X, CompanyStage.ROYALTY: I},
    "burn_as_pct_of_market_cap": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: R, CompanyStage.PRODUCER: I, CompanyStage.ROYALTY: I},
    "working_capital": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: C, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: X},
    "cash_per_share": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: R, CompanyStage.PRODUCER: X, CompanyStage.ROYALTY: X},
    "ncav_per_share": {CompanyStage.GRASSROOTS: R, CompanyStage.EXPLORER: R, CompanyStage.DEVELOPER: X, CompanyStage.PRODUCER: X, CompanyStage.ROYALTY: I},
    "current_ratio": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: C, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    "quick_ratio": {CompanyStage.GRASSROOTS: R, CompanyStage.EXPLORER: R, CompanyStage.DEVELOPER: R, CompanyStage.PRODUCER: X, CompanyStage.ROYALTY: X},
    "debt_to_equity": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: C, CompanyStage.PRODUCER: M, CompanyStage.ROYALTY: M},
    "debt_to_ebitda": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: X, CompanyStage.PRODUCER: C, CompanyStage.ROYALTY: R},
    "interest_coverage": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: X, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: X},
    "altman_z_score": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: X, CompanyStage.DEVELOPER: X, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: X},
    "debt_per_share": {CompanyStage.GRASSROOTS: R, CompanyStage.EXPLORER: R, CompanyStage.DEVELOPER: R, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: X},
    "debt_service_coverage": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: X, CompanyStage.PRODUCER: C, CompanyStage.ROYALTY: R},
    # GROWTH
    "shares_growth_yoy": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: C, CompanyStage.PRODUCER: M, CompanyStage.ROYALTY: M},
    "shares_growth_3y_cagr": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: C, CompanyStage.PRODUCER: X, CompanyStage.ROYALTY: X},
    "revenue_growth_yoy": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: C, CompanyStage.ROYALTY: C},
    "revenue_cagr_3y": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    "revenue_cagr_5y": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: X, CompanyStage.ROYALTY: X},
    "earnings_growth_yoy": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    "earnings_cagr_3y": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: X, CompanyStage.ROYALTY: X},
    "earnings_cagr_5y": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: X, CompanyStage.ROYALTY: X},
    "book_value_growth_yoy": {CompanyStage.GRASSROOTS: R, CompanyStage.EXPLORER: R, CompanyStage.DEVELOPER: R, CompanyStage.PRODUCER: X, CompanyStage.ROYALTY: X},
    "fcf_growth_yoy": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    "capex_to_revenue": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: X, CompanyStage.PRODUCER: C, CompanyStage.ROYALTY: I},
    "capex_to_ocf": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: X, CompanyStage.PRODUCER: C, CompanyStage.ROYALTY: X},
    "reinvestment_rate": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: X, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: X},
    "dividend_payout_ratio": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: C},
    "dividend_coverage": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: C},
    "shareholder_yield": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    "fcf_per_share": {CompanyStage.GRASSROOTS: I, CompanyStage.EXPLORER: I, CompanyStage.DEVELOPER: I, CompanyStage.PRODUCER: C, CompanyStage.ROYALTY: C},
    "ocf_per_share": {CompanyStage.GRASSROOTS: X, CompanyStage.EXPLORER: X, CompanyStage.DEVELOPER: R, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    # ENERGY QUALITY
    "quality_score": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: C, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    "insider_alignment": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: C, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    "financial_position": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: C, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: X},
    "dilution_risk": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: C, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: X},
    "asset_backing": {CompanyStage.GRASSROOTS: R, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: R, CompanyStage.PRODUCER: X, CompanyStage.ROYALTY: I},
    "revenue_predictability": {CompanyStage.GRASSROOTS: X, CompanyStage.EXPLORER: X, CompanyStage.DEVELOPER: X, CompanyStage.PRODUCER: C, CompanyStage.ROYALTY: C},
    # SHARE STRUCTURE
    "shares_outstanding": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: R, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: X},
    "fully_diluted_shares": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: C, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: X},
    "insider_ownership_pct": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: C, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    "institutional_ownership_pct": {CompanyStage.GRASSROOTS: R, CompanyStage.EXPLORER: R, CompanyStage.DEVELOPER: R, CompanyStage.PRODUCER: R, CompanyStage.ROYALTY: R},
    "share_structure_assessment": {CompanyStage.GRASSROOTS: C, CompanyStage.EXPLORER: C, CompanyStage.DEVELOPER: R, CompanyStage.PRODUCER: X, CompanyStage.ROYALTY: X},
}


# ======================================================================
# Tier-based relevance tables (fallback when no stage override exists)
# ======================================================================

VALUATION_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "pe_trailing":           {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: R, CompanyTier.MICRO: X, CompanyTier.NANO: I},
    "pb_ratio":              {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "ps_ratio":              {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: R, CompanyTier.SMALL: R, CompanyTier.MICRO: X, CompanyTier.NANO: I},
    "p_fcf":                 {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: R, CompanyTier.MICRO: X, CompanyTier.NANO: I},
    "ev_ebitda":             {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: R, CompanyTier.MICRO: X, CompanyTier.NANO: I},
    "cash_to_market_cap":    {CompanyTier.MEGA: I, CompanyTier.LARGE: I, CompanyTier.MID: X, CompanyTier.SMALL: R, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "price_to_tangible_book":{CompanyTier.MEGA: X, CompanyTier.LARGE: X, CompanyTier.MID: R, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "price_to_ncav":         {CompanyTier.MEGA: I, CompanyTier.LARGE: I, CompanyTier.MID: X, CompanyTier.SMALL: R, CompanyTier.MICRO: C, CompanyTier.NANO: C},
}

PROFITABILITY_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "roe":              {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: R, CompanyTier.MICRO: X, CompanyTier.NANO: I},
    "roic":             {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: R, CompanyTier.MICRO: X, CompanyTier.NANO: I},
    "gross_margin":     {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: R, CompanyTier.NANO: X},
    "fcf_margin":       {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: R, CompanyTier.SMALL: R, CompanyTier.MICRO: X, CompanyTier.NANO: I},
}

SOLVENCY_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "debt_to_equity":    {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "current_ratio":     {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: R, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "cash_burn_rate":    {CompanyTier.MEGA: I, CompanyTier.LARGE: I, CompanyTier.MID: X, CompanyTier.SMALL: R, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "cash_runway_years": {CompanyTier.MEGA: I, CompanyTier.LARGE: I, CompanyTier.MID: X, CompanyTier.SMALL: R, CompanyTier.MICRO: C, CompanyTier.NANO: C},
}

GROWTH_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "shares_growth_yoy":      {CompanyTier.MEGA: X, CompanyTier.LARGE: X, CompanyTier.MID: R, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "revenue_growth_yoy":     {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
}

ENERGY_QUALITY_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "quality_score":          {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: R, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "insider_alignment":      {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: R, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
}

SHARE_STRUCTURE_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "shares_outstanding":       {CompanyTier.MEGA: X, CompanyTier.LARGE: X, CompanyTier.MID: R, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "fully_diluted_shares":     {CompanyTier.MEGA: X, CompanyTier.LARGE: X, CompanyTier.MID: R, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "insider_ownership_pct":    {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: R, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
}
