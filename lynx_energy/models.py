"""Data models for Lynx Energy — energy-focused fundamental analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Company tier classification (market cap based)
# ---------------------------------------------------------------------------

class CompanyTier(str, Enum):
    MEGA = "Mega Cap"
    LARGE = "Large Cap"
    MID = "Mid Cap"
    SMALL = "Small Cap"
    MICRO = "Micro Cap"
    NANO = "Nano Cap"


def classify_tier(market_cap: Optional[float]) -> CompanyTier:
    if market_cap is None or market_cap <= 0:
        return CompanyTier.NANO
    if market_cap >= 200_000_000_000:
        return CompanyTier.MEGA
    if market_cap >= 10_000_000_000:
        return CompanyTier.LARGE
    if market_cap >= 2_000_000_000:
        return CompanyTier.MID
    if market_cap >= 300_000_000:
        return CompanyTier.SMALL
    if market_cap >= 50_000_000:
        return CompanyTier.MICRO
    return CompanyTier.NANO


# ---------------------------------------------------------------------------
# Energy company stage classification
# ---------------------------------------------------------------------------

class CompanyStage(str, Enum):
    GRASSROOTS = "Early Exploration"
    EXPLORER = "Advanced Explorer"
    DEVELOPER = "Developer"
    PRODUCER = "Producer"
    ROYALTY = "Royalty/Streaming"


class Commodity(str, Enum):
    CRUDE_OIL = "Crude Oil"
    NATURAL_GAS = "Natural Gas"
    LNG = "LNG"
    NGL = "NGL"
    URANIUM = "Uranium"
    COAL = "Coal"
    HYDROGEN = "Hydrogen"
    RENEWABLE = "Renewable Energy"
    OTHER = "Other"


class JurisdictionTier(str, Enum):
    TIER_1 = "Tier 1 — Low Risk"
    TIER_2 = "Tier 2 — Moderate Risk"
    TIER_3 = "Tier 3 — High Risk"
    UNKNOWN = "Unknown"


class Relevance(str, Enum):
    CRITICAL = "critical"
    RELEVANT = "relevant"
    CONTEXTUAL = "contextual"
    IRRELEVANT = "irrelevant"


# ---------------------------------------------------------------------------
# Core data models
# ---------------------------------------------------------------------------

@dataclass
class CompanyProfile:
    ticker: str
    name: str
    isin: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    exchange: Optional[str] = None
    currency: Optional[str] = None
    market_cap: Optional[float] = None
    description: Optional[str] = None
    website: Optional[str] = None
    employees: Optional[int] = None
    tier: CompanyTier = CompanyTier.NANO
    stage: CompanyStage = CompanyStage.GRASSROOTS
    primary_commodity: Commodity = Commodity.OTHER
    jurisdiction_tier: JurisdictionTier = JurisdictionTier.UNKNOWN
    jurisdiction_country: Optional[str] = None


@dataclass
class ValuationMetrics:
    pe_trailing: Optional[float] = None
    pe_forward: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    p_fcf: Optional[float] = None
    ev_ebitda: Optional[float] = None
    ev_revenue: Optional[float] = None
    peg_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    earnings_yield: Optional[float] = None
    enterprise_value: Optional[float] = None
    market_cap: Optional[float] = None
    price_to_tangible_book: Optional[float] = None
    price_to_ncav: Optional[float] = None
    ev_per_boe: Optional[float] = None
    ev_per_mcfe: Optional[float] = None
    p_nav: Optional[float] = None
    cash_to_market_cap: Optional[float] = None
    nav_per_share: Optional[float] = None


@dataclass
class ProfitabilityMetrics:
    roe: Optional[float] = None
    roa: Optional[float] = None
    roic: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    fcf_margin: Optional[float] = None
    ebitda_margin: Optional[float] = None
    netback_per_boe: Optional[float] = None
    netback_unit: str = "boe"
    operating_cost_per_boe: Optional[float] = None
    netback_margin: Optional[float] = None


@dataclass
class SolvencyMetrics:
    debt_to_equity: Optional[float] = None
    debt_to_ebitda: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    interest_coverage: Optional[float] = None
    altman_z_score: Optional[float] = None
    net_debt: Optional[float] = None
    total_debt: Optional[float] = None
    total_cash: Optional[float] = None
    cash_burn_rate: Optional[float] = None
    cash_runway_years: Optional[float] = None
    working_capital: Optional[float] = None
    cash_per_share: Optional[float] = None
    tangible_book_value: Optional[float] = None
    ncav: Optional[float] = None
    ncav_per_share: Optional[float] = None
    quarterly_burn_rate: Optional[float] = None
    burn_as_pct_of_market_cap: Optional[float] = None


@dataclass
class GrowthMetrics:
    revenue_growth_yoy: Optional[float] = None
    revenue_cagr_3y: Optional[float] = None
    revenue_cagr_5y: Optional[float] = None
    earnings_growth_yoy: Optional[float] = None
    earnings_cagr_3y: Optional[float] = None
    earnings_cagr_5y: Optional[float] = None
    fcf_growth_yoy: Optional[float] = None
    book_value_growth_yoy: Optional[float] = None
    dividend_growth_5y: Optional[float] = None
    shares_growth_yoy: Optional[float] = None
    shares_growth_3y_cagr: Optional[float] = None
    fully_diluted_shares: Optional[float] = None
    dilution_ratio: Optional[float] = None
    production_growth_yoy: Optional[float] = None


@dataclass
class EfficiencyMetrics:
    asset_turnover: Optional[float] = None
    inventory_turnover: Optional[float] = None
    receivables_turnover: Optional[float] = None
    days_sales_outstanding: Optional[float] = None
    days_inventory: Optional[float] = None
    cash_conversion_cycle: Optional[float] = None


@dataclass
class EnergyQualityIndicators:
    quality_score: Optional[float] = None
    management_quality: Optional[str] = None
    insider_ownership_pct: Optional[float] = None
    management_track_record: Optional[str] = None
    jurisdiction_assessment: Optional[str] = None
    jurisdiction_score: Optional[float] = None
    reserve_quality: Optional[str] = None
    reserve_life_assessment: Optional[str] = None
    production_scale_assessment: Optional[str] = None
    financial_position: Optional[str] = None
    dilution_risk: Optional[str] = None
    share_structure_assessment: Optional[str] = None
    catalyst_density: Optional[str] = None
    near_term_catalysts: list[str] = field(default_factory=list)
    strategic_backing: Optional[str] = None
    competitive_position: Optional[str] = None
    asset_backing: Optional[str] = None
    niche_position: Optional[str] = None
    insider_alignment: Optional[str] = None
    revenue_predictability: Optional[str] = None
    roic_history: list[Optional[float]] = field(default_factory=list)
    gross_margin_history: list[Optional[float]] = field(default_factory=list)


@dataclass
class IntrinsicValue:
    dcf_value: Optional[float] = None
    graham_number: Optional[float] = None
    lynch_fair_value: Optional[float] = None
    ncav_value: Optional[float] = None
    asset_based_value: Optional[float] = None
    nav_per_share: Optional[float] = None
    ev_reserve_implied_price: Optional[float] = None
    current_price: Optional[float] = None
    margin_of_safety_dcf: Optional[float] = None
    margin_of_safety_graham: Optional[float] = None
    margin_of_safety_ncav: Optional[float] = None
    margin_of_safety_asset: Optional[float] = None
    margin_of_safety_nav: Optional[float] = None
    primary_method: Optional[str] = None
    secondary_method: Optional[str] = None


@dataclass
class ShareStructure:
    shares_outstanding: Optional[float] = None
    fully_diluted_shares: Optional[float] = None
    warrants_outstanding: Optional[float] = None
    options_outstanding: Optional[float] = None
    insider_ownership_pct: Optional[float] = None
    institutional_ownership_pct: Optional[float] = None
    float_shares: Optional[float] = None
    share_structure_assessment: Optional[str] = None
    warrant_overhang_risk: Optional[str] = None


@dataclass
class InsiderTransaction:
    """A single insider buy/sell transaction."""
    insider: str = ""
    position: str = ""
    transaction_type: str = ""
    shares: Optional[float] = None
    value: Optional[float] = None
    date: str = ""


@dataclass
class MarketIntelligence:
    """Market sentiment, insider activity, institutional holdings, and technicals.

    This section aggregates signals that are especially important for
    energy investors: insider buying in juniors is a strong signal, short
    interest indicates sentiment, and analyst targets provide a consensus
    reference for commodity-sensitive stocks.
    """
    # Insider activity
    insider_transactions: list[InsiderTransaction] = field(default_factory=list)
    net_insider_shares_3m: Optional[float] = None
    insider_buy_signal: Optional[str] = None

    # Institutional holders
    top_holders: list[str] = field(default_factory=list)
    institutions_count: Optional[int] = None
    institutions_pct: Optional[float] = None

    # Analyst consensus
    analyst_count: Optional[int] = None
    recommendation: Optional[str] = None
    target_high: Optional[float] = None
    target_low: Optional[float] = None
    target_mean: Optional[float] = None
    target_upside_pct: Optional[float] = None

    # Short interest
    shares_short: Optional[float] = None
    short_pct_of_float: Optional[float] = None
    short_ratio_days: Optional[float] = None
    short_squeeze_risk: Optional[str] = None

    # Price technicals
    price_current: Optional[float] = None
    price_52w_high: Optional[float] = None
    price_52w_low: Optional[float] = None
    pct_from_52w_high: Optional[float] = None
    pct_from_52w_low: Optional[float] = None
    price_52w_range_position: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    above_sma_50: Optional[bool] = None
    above_sma_200: Optional[bool] = None
    golden_cross: Optional[bool] = None
    beta: Optional[float] = None
    avg_volume: Optional[float] = None
    volume_10d_avg: Optional[float] = None
    volume_trend: Optional[str] = None

    # Projected dilution (for pre-revenue energy companies)
    projected_dilution_annual_pct: Optional[float] = None
    projected_shares_in_2y: Optional[float] = None
    financing_warning: Optional[str] = None

    # Commodity market context
    commodity_name: Optional[str] = None
    commodity_price: Optional[float] = None
    commodity_currency: str = "USD"
    commodity_52w_high: Optional[float] = None
    commodity_52w_low: Optional[float] = None
    commodity_52w_position: Optional[float] = None
    commodity_ytd_change: Optional[float] = None

    # Sector ETF context
    sector_etf_name: Optional[str] = None
    sector_etf_ticker: Optional[str] = None
    sector_etf_price: Optional[float] = None
    sector_etf_3m_perf: Optional[float] = None
    peer_etf_name: Optional[str] = None
    peer_etf_ticker: Optional[str] = None
    peer_etf_price: Optional[float] = None
    peer_etf_3m_perf: Optional[float] = None

    # Risk warnings
    risk_warnings: list[str] = field(default_factory=list)

    # Energy-specific disclaimers
    disclaimers: list[str] = field(default_factory=list)


@dataclass
class FinancialStatement:
    period: str
    revenue: Optional[float] = None
    cost_of_revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_income: Optional[float] = None
    net_income: Optional[float] = None
    ebitda: Optional[float] = None
    interest_expense: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    total_equity: Optional[float] = None
    total_debt: Optional[float] = None
    total_cash: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    capital_expenditure: Optional[float] = None
    free_cash_flow: Optional[float] = None
    dividends_paid: Optional[float] = None
    shares_outstanding: Optional[float] = None
    eps: Optional[float] = None
    book_value_per_share: Optional[float] = None
    exploration_expenditure: Optional[float] = None
    oil_gas_properties: Optional[float] = None


@dataclass
class AnalysisConclusion:
    overall_score: float = 0.0
    verdict: str = ""
    summary: str = ""
    category_scores: dict = field(default_factory=dict)
    category_summaries: dict = field(default_factory=dict)
    strengths: list = field(default_factory=list)
    risks: list = field(default_factory=list)
    tier_note: str = ""
    stage_note: str = ""
    screening_checklist: dict = field(default_factory=dict)


@dataclass
class MetricExplanation:
    key: str
    full_name: str
    description: str
    why_used: str
    formula: str
    category: str


@dataclass
class Filing:
    form_type: str
    filing_date: str
    period: str
    url: str
    description: Optional[str] = None
    local_path: Optional[str] = None


@dataclass
class NewsArticle:
    title: str
    url: str
    published: Optional[str] = None
    source: Optional[str] = None
    summary: Optional[str] = None
    local_path: Optional[str] = None


@dataclass
class AnalysisReport:
    profile: CompanyProfile
    valuation: Optional[ValuationMetrics] = None
    profitability: Optional[ProfitabilityMetrics] = None
    solvency: Optional[SolvencyMetrics] = None
    growth: Optional[GrowthMetrics] = None
    efficiency: Optional[EfficiencyMetrics] = None
    energy_quality: Optional[EnergyQualityIndicators] = None
    intrinsic_value: Optional[IntrinsicValue] = None
    share_structure: Optional[ShareStructure] = None
    market_intelligence: Optional[MarketIntelligence] = None
    financials: list[FinancialStatement] = field(default_factory=list)
    filings: list[Filing] = field(default_factory=list)
    news: list[NewsArticle] = field(default_factory=list)
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ---------------------------------------------------------------------------
# Stage classification helpers
# ---------------------------------------------------------------------------

_STAGE_KEYWORDS = {
    CompanyStage.PRODUCER: [
        "production", "producing", "operations", "refinery", "processing",
        "netback", "operating cost per", "barrels per day", "boe/d",
        "mcfe/d", "pipeline", "midstream operations", "throughput",
    ],
    CompanyStage.DEVELOPER: [
        "feasibility study", "pre-feasibility", "field development plan",
        "construction", "development stage", "permitting", "environmental assessment",
        "FID", "final investment decision", "front-end engineering",
        "development and production", "exploration and development",
    ],
    CompanyStage.EXPLORER: [
        "resource estimate", "proved reserves", "probable reserves",
        "prospective resources", "contingent resources", "seismic survey",
        "appraisal well", "discovery well", "advanced exploration",
        "2P reserves", "3P reserves",
    ],
    CompanyStage.GRASSROOTS: [
        "exploration", "grassroots", "prospecting", "drill program",
        "early stage", "target generation", "acreage", "land position",
        "seismic acquisition", "wildcat",
    ],
}

_COMMODITY_KEYWORDS = {
    Commodity.CRUDE_OIL: ["crude oil", "oil", "petroleum", "brent", "wti", "bitumen", "oil sands"],
    Commodity.NATURAL_GAS: ["natural gas", "methane", "shale gas", "gas production", "gas wells"],
    Commodity.LNG: ["lng", "liquefied natural gas", "liquefaction", "lng export", "lng terminal"],
    Commodity.NGL: ["ngl", "natural gas liquids", "condensate", "propane", "butane"],
    Commodity.URANIUM: ["uranium", "u3o8", "nuclear", "yellowcake"],
    Commodity.COAL: ["coal", "thermal coal", "metallurgical coal", "coking coal"],
    Commodity.HYDROGEN: ["hydrogen", "h2", "green hydrogen", "blue hydrogen", "electrolysis"],
    Commodity.RENEWABLE: ["solar", "wind", "renewable", "geothermal", "hydroelectric", "biomass"],
}

_TIER_1_JURISDICTIONS = {
    "canada", "alberta", "british columbia", "saskatchewan",
    "united states", "texas", "north dakota", "oklahoma", "colorado",
    "new mexico", "wyoming", "louisiana", "pennsylvania",
    "australia", "western australia", "queensland",
    "norway", "united kingdom", "denmark",
}

_TIER_2_JURISDICTIONS = {
    "mexico", "brazil", "colombia", "argentina", "guyana",
    "malaysia", "indonesia", "india", "china",
    "egypt", "ghana", "mozambique", "tanzania",
    "romania", "turkey", "kazakhstan",
}


def classify_stage(description: Optional[str], revenue: Optional[float],
                   info: Optional[dict] = None) -> CompanyStage:
    if description is None:
        description = ""
    desc_lower = description.lower()

    if revenue is not None and revenue > 10_000_000:
        import re as _re
        for pattern in [r"\broyalty\b", r"\bstreaming\b", r"\broyalty.{0,5}company\b"]:
            if _re.search(pattern, desc_lower):
                return CompanyStage.ROYALTY
        for kw in _STAGE_KEYWORDS[CompanyStage.PRODUCER]:
            if kw.lower() in desc_lower:
                return CompanyStage.PRODUCER
        # Revenue-generating company with no stage keywords defaults to Producer
        return CompanyStage.PRODUCER

    for stage in [CompanyStage.DEVELOPER,
                  CompanyStage.EXPLORER, CompanyStage.GRASSROOTS]:
        for kw in _STAGE_KEYWORDS[stage]:
            if kw.lower() in desc_lower:
                return stage

    # Check PRODUCER keywords last in the fallback (no revenue threshold met)
    for kw in _STAGE_KEYWORDS[CompanyStage.PRODUCER]:
        if kw.lower() in desc_lower:
            return CompanyStage.PRODUCER

    if info:
        industry = (info.get("industry") or "").lower()
        if "oil" in industry or "gas" in industry or "energy" in industry:
            return CompanyStage.EXPLORER

    return CompanyStage.GRASSROOTS


def classify_commodity(description: Optional[str],
                       industry: Optional[str] = None) -> Commodity:
    import re
    text = ((description or "") + " " + (industry or "")).lower()
    scores: dict[Commodity, int] = {}
    for commodity, keywords in _COMMODITY_KEYWORDS.items():
        count = 0
        for kw in keywords:
            kw_lower = kw.lower()
            # Use word boundary matching for short keywords to avoid false matches
            if len(kw_lower) <= 3:
                if re.search(r'\b' + re.escape(kw_lower) + r'\b', text):
                    count += 1
            else:
                if kw_lower in text:
                    count += 1
        if count > 0:
            scores[commodity] = count
    if scores:
        return max(scores, key=scores.get)
    return Commodity.OTHER


def classify_jurisdiction(country: Optional[str],
                          description: Optional[str] = None) -> JurisdictionTier:
    import re as _re
    if not country:
        return JurisdictionTier.UNKNOWN
    c_lower = country.lower().strip()
    # Only check country field with substring (country names are reliable)
    # Use word-boundary for description to avoid false positives (e.g. "india" in "Indiana")
    for j in _TIER_1_JURISDICTIONS:
        if j in c_lower:
            return JurisdictionTier.TIER_1
    for j in _TIER_2_JURISDICTIONS:
        if j in c_lower:
            return JurisdictionTier.TIER_2
    # Fallback: check description with word boundaries
    if description:
        desc_lower = description.lower()
        for j in _TIER_1_JURISDICTIONS:
            if _re.search(r'\b' + _re.escape(j) + r'\b', desc_lower):
                return JurisdictionTier.TIER_1
        for j in _TIER_2_JURISDICTIONS:
            if _re.search(r'\b' + _re.escape(j) + r'\b', desc_lower):
                return JurisdictionTier.TIER_2
    return JurisdictionTier.TIER_3
