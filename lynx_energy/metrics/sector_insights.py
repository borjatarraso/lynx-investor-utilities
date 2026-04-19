"""Energy-focused sector and industry insights."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SectorInsight:
    sector: str; overview: str; critical_metrics: list[str] = field(default_factory=list)
    key_risks: list[str] = field(default_factory=list); what_to_watch: list[str] = field(default_factory=list)
    typical_valuation: str = ""

@dataclass
class IndustryInsight:
    industry: str; sector: str; overview: str; critical_metrics: list[str] = field(default_factory=list)
    key_risks: list[str] = field(default_factory=list); what_to_watch: list[str] = field(default_factory=list)
    typical_valuation: str = ""

_SECTORS: dict[str, SectorInsight] = {}
_INDUSTRIES: dict[str, IndustryInsight] = {}

def _add_sector(sector, overview, cm, kr, wtw, tv):
    _SECTORS[sector.lower()] = SectorInsight(sector=sector, overview=overview, critical_metrics=cm, key_risks=kr, what_to_watch=wtw, typical_valuation=tv)

def _add_industry(industry, sector, overview, cm, kr, wtw, tv):
    _INDUSTRIES[industry.lower()] = IndustryInsight(industry=industry, sector=sector, overview=overview, critical_metrics=cm, key_risks=kr, what_to_watch=wtw, typical_valuation=tv)

_add_sector("Energy",
    "Energy companies are commodity-driven and highly cyclical. Oil, gas, uranium, and coal prices dominate valuations. Balance sheet strength is critical to survive price downturns. Junior E&P companies are effectively venture capital — high risk, high reward. Capital discipline and reserve replacement are key long-term drivers.",
    ["EV/EBITDA for producers", "FCF Yield", "Debt/EBITDA", "Reserve Life Index", "Breakeven Price", "Cash Runway for explorers", "Share Dilution Rate"],
    ["Commodity price collapse", "Regulatory/environmental risk", "Energy transition uncertainty", "Geopolitical risk", "Decline rate risk", "Capital cost overruns"],
    ["Oil/gas/uranium supply-demand fundamentals", "OPEC+ decisions and production quotas", "Capital discipline and shareholder returns", "Reserve replacement ratio", "Insider buying/selling", "ESG and energy transition policy"],
    "EV/EBITDA 4-8 for producers. FCF yield is the best valuation anchor. P/E unreliable due to commodity cycles. EV/BOE for E&P reserves.")

_add_industry("Oil & Gas E&P", "Energy",
    "Exploration and production companies are leveraged to oil and gas prices. Breakeven cost, reserve life, and decline rates determine profitability. Junior E&P explorers are valued on acreage, prospective resources, and management track record. Producers are valued on cash flow and reserves.",
    ["Breakeven Price per BOE", "Reserve Life Index (years)", "Decline Rate", "F&D Cost per BOE", "EV/BOE of 2P Reserves", "FCF Yield"],
    ["Oil/gas price decline", "Decline rates requiring constant reinvestment", "Regulatory/environmental risk", "Drilling dry holes", "Access to capital for juniors"],
    ["WTI/Brent/Henry Hub price cycles", "Rig count trends", "Well results and reserve additions", "Capital discipline vs growth spending", "Insider buying in juniors"],
    "EV/EBITDA 3-6 for producers. EV/BOE $5-15 for proved reserves. FCF yield >10% is attractive. P/NAV 0.5-1.0x for developers.")

_add_industry("Oil & Gas Integrated", "Energy",
    "Integrated oil & gas majors have upstream (E&P), midstream, and downstream (refining/marketing) operations. Diversification provides earnings stability. These companies typically offer strong dividends and buybacks during high-price cycles.",
    ["FCF Yield", "Dividend Yield & Sustainability", "ROIC", "Debt/EBITDA", "Reserve Replacement Ratio"],
    ["Energy transition risk reducing long-term demand", "Regulatory carbon costs", "Political risk in operating jurisdictions", "Mega-project cost overruns", "Stranded asset risk"],
    ["Capital allocation: dividends vs buybacks vs capex", "Downstream margin cycles", "Carbon intensity reduction plans", "Natural gas/LNG strategy", "Portfolio high-grading"],
    "EV/EBITDA 4-7. FCF yield 8-12% at mid-cycle. Dividend yield 3-6%. P/E less reliable. Sum-of-parts for diverse portfolios.")

_add_industry("Oil & Gas Midstream", "Energy",
    "Midstream companies operate pipelines, gathering systems, processing plants, and storage. Revenue is largely fee-based with commodity exposure varying by contract type. MLPs and corporations both common. Valued on distributable cash flow.",
    ["Distributable Cash Flow (DCF)", "Distribution Coverage Ratio", "Debt/EBITDA", "Contract Mix (fee vs commodity)", "Volume Growth"],
    ["Volume declines in connected basins", "Regulatory pipeline permitting challenges", "Interest rate sensitivity (high leverage)", "Customer concentration risk", "Energy transition long-term demand"],
    ["Basin production growth trajectories", "New pipeline/plant construction", "Distribution growth and coverage", "Debt reduction plans", "Contract renewals and recontracting risk"],
    "EV/EBITDA 8-12. Yield 5-8% with 1.2x+ coverage. P/DCF is primary. Lower EV/EBITDA for gathering-focused, higher for long-haul pipelines.")

_add_industry("Oil & Gas Refining & Marketing", "Energy",
    "Refiners convert crude oil into gasoline, diesel, jet fuel, and petrochemicals. Profitability depends on crack spreads (product price minus crude cost), not absolute oil prices. High capital intensity with multi-year margin cycles.",
    ["Crack Spread Margins", "Refinery Utilization Rate", "Complexity Index (Nelson)", "FCF Yield", "Debt/EBITDA"],
    ["Crack spread compression", "Environmental regulations and carbon costs", "EV penetration reducing gasoline demand", "Unplanned downtime and maintenance costs", "Feedstock quality changes"],
    ["Gasoline/diesel demand trends", "Refinery closures and capacity rationalization", "Petrochemical integration", "Renewable diesel/SAF investments", "Seasonal crack spread patterns"],
    "EV/EBITDA 3-5 (low vs other energy). P/E used at mid-cycle. FCF yield >10% is compelling. Dividend yield 3-5% for majors.")

_add_industry("Oil & Gas Equipment & Services", "Energy",
    "Oilfield services companies provide drilling, completion, production, and maintenance services to E&P operators. Revenue is driven by upstream capital spending cycles. High operating leverage — margins expand rapidly when rig counts rise.",
    ["Revenue per Rig", "EBITDA Margin Trend", "Backlog/Book-to-Bill", "Rig Count Correlation", "FCF Conversion"],
    ["Upstream capex cuts during downturns", "Overcapacity and pricing pressure", "Technology disruption (e.g., longer laterals)", "International execution risk", "Working capital intensity"],
    ["North American and international rig counts", "E&P capital spending guidance", "Day rates and service pricing trends", "Technology adoption", "Consolidation and market share shifts"],
    "EV/EBITDA 5-8. P/E at normalized earnings. Revenue multiples for growth-phase companies. Higher multiples for technology-differentiated services.")

_add_industry("Uranium", "Energy",
    "Uranium producers benefit from nuclear fleet growth and structural supply deficit. Contract vs spot dynamics are critical. Long development timelines. ISR (in-situ recovery) vs conventional mining affects cost profile significantly. Included in energy sector due to nuclear power generation focus.",
    ["EV/lb U3O8 in ground", "Contract vs spot exposure", "Production cost per lb", "Cash Runway", "Permitting status"],
    ["Uranium price volatility", "Political/regulatory sentiment toward nuclear", "Long permitting timelines (5-15 years)", "Construction cost overruns", "Water rights and environmental issues"],
    ["Nuclear fleet growth (China, India)", "US/EU nuclear renaissance policy", "Supply deficit projections", "Sprott Physical Uranium Trust inventory", "Contract pricing vs spot"],
    "EV/lb of resource. P/NAV from feasibility studies. ISR producers trade at premium due to lower capex. Producers: EV/EBITDA 6-10.")

_add_industry("Thermal Coal", "Energy",
    "Thermal coal producers supply fuel for coal-fired power generation. Facing long-term structural decline in developed markets due to energy transition, but growing demand in Asia. Valued on cash flow with limited reinvestment. ESG constraints limit investor base.",
    ["Cash Cost per Tonne", "Reserve Life", "Contracted vs Spot Sales", "FCF Yield", "Debt/EBITDA"],
    ["Energy transition and coal plant retirements", "ESG-driven divestment reducing access to capital", "Regulatory carbon costs", "Transportation bottlenecks", "Weather and demand seasonality"],
    ["Asian import demand (India, Southeast Asia)", "Coal plant closure schedules", "Alternative fuel substitution rates", "Carbon credit costs", "Seaborne vs domestic pricing"],
    "EV/EBITDA 2-4 (depressed due to ESG discount). FCF yield 15-25% common. Dividend yield 5-10%+. Terminal value assumptions are critical.")

_add_industry("Solar", "Energy",
    "Solar energy companies manufacture panels, develop utility-scale projects, or provide distributed rooftop installations. High growth but capital-intensive. Subsidy sensitivity and technology learning curves drive economics. Module pricing is highly competitive.",
    ["Levelized Cost of Energy (LCOE)", "Backlog/Pipeline GW", "Module Efficiency Trend", "Revenue Growth", "Gross Margin"],
    ["Module price deflation", "Subsidy/tariff policy changes", "Interest rate sensitivity for project financing", "Supply chain concentration (polysilicon)", "Grid interconnection bottlenecks"],
    ["ITC/PTC policy extensions", "Utility-scale procurement pipelines", "Battery storage integration", "Module efficiency improvements", "Domestic manufacturing incentives"],
    "EV/Revenue 1-3x. P/E 15-30 for profitable companies. DCF with long-term contracted cash flows. Pipeline/backlog is key forward indicator.")

def get_sector_insight(sector: str | None) -> SectorInsight | None:
    return _SECTORS.get(sector.lower()) if sector else None

def get_industry_insight(industry: str | None) -> IndustryInsight | None:
    return _INDUSTRIES.get(industry.lower()) if industry else None

def list_sectors() -> list[str]:
    return sorted(s.sector for s in _SECTORS.values())

def list_industries() -> list[str]:
    return sorted(i.industry for i in _INDUSTRIES.values())
