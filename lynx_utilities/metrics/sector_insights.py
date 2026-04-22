"""Utilities-focused sector and industry insights."""

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

_add_sector("Utilities",
    "Utilities are capital-intensive, rate-base-driven businesses with low but stable growth. Regulated utilities earn an allowed return on a regulator-approved asset base; their earnings quality depends on the constructiveness of the regulatory compact, the cadence of rate cases, and the ability to recover capex in rates. Independent power producers (IPPs) and merchant generators face commodity and power-price exposure. Utilities are deeply levered — investment-grade credit is a prerequisite — and sensitive to interest rates, which drive both the allowed ROE and the sector's valuation multiple.",
    ["Rate Base Growth (CAGR)", "Earned ROE vs Allowed ROE", "FFO / Debt", "FFO Interest Coverage", "Dividend Coverage (FCF)", "Capex / Revenue", "Debt / EBITDA"],
    ["Unfavourable rate case outcomes", "Interest rate risk (discount-rate & refinancing)", "Regulatory lag eroding returns", "Large capex program execution risk", "Wildfire / storm / environmental liabilities", "Stranded assets from decarbonization", "Weather-driven demand volatility"],
    ["State / national rate case calendars", "Allowed ROE decisions vs cost-of-capital", "Credit rating outlook and FFO/Debt ratios", "Capex program progress and recovery mechanisms", "Load growth (data centres, electrification)", "Decarbonization / IRP filings", "Interest-rate direction and bond-yield differentials"],
    "P/E 14-20x for regulated operators. EV/EBITDA 9-12x. FFO/Debt >14% for investment-grade. Dividend yield 3-5% with 3-6% dividend CAGR. IPPs trade at EV/EBITDA 6-9x on merchant exposure.")

_add_industry("Utilities — Regulated Electric", "Utilities",
    "Regulated electric utilities earn a regulator-approved return on a rate base of transmission, distribution and (in some jurisdictions) generation assets. Earnings compound with rate-base growth; high-quality names grow rate base 6-9% annually through capex programs for grid hardening, electrification, and renewables. Regulatory constructiveness is the primary moat.",
    ["Rate Base Growth (CAGR)", "Allowed ROE vs Earned ROE", "Regulatory Lag", "Equity Layer / Capital Structure", "EPS Growth Guidance", "Dividend Coverage", "FFO / Debt"],
    ["Adverse rate case outcomes (lower allowed ROE or equity layer)", "Regulatory lag reducing earned returns below allowed", "Storm / wildfire cost disallowance", "Interest rate spikes compressing P/E multiples", "Customer bill affordability pushback", "Decarbonization capex with uncertain recovery"],
    ["State PUC rate case filings and orders", "Integrated Resource Plan (IRP) updates", "Capex guidance and 5-year plans", "Earnings vs allowed ROE gap", "Dividend growth rate alignment with EPS growth", "Investment-grade rating outlook"],
    "P/E 16-20x at investment-grade. P/B 1.7-2.2x (premium for rate-base growth). EV/EBITDA 10-12x. Dividend yield 3.5-4.5%. FFO/Debt 14-17%.")

_add_industry("Utilities — Regulated Gas", "Utilities",
    "Regulated gas utilities (local distribution companies, or LDCs) deliver natural gas to residential, commercial and industrial customers under regulator-approved rates. Revenue decoupling mechanisms isolate earnings from weather and volumes in many jurisdictions. Capex focuses on pipeline safety, system modernization and, increasingly, RNG / hydrogen blending pilots. Long-term electrification risk is the primary structural concern.",
    ["Rate Base Growth", "Allowed ROE / Equity Layer", "Decoupling Mechanisms", "Capex / Revenue", "Debt / EBITDA", "Dividend Coverage", "FFO / Debt"],
    ["Electrification policy (gas hook-up bans)", "Pipeline safety incidents and liabilities", "Rate case disallowances on capex", "Long-term demand destruction in buildings", "Methane regulation costs", "Interest-rate compression on multiple"],
    ["State gas-ban / electrification policy", "Pipeline integrity capex recovery", "Customer count growth and defection rates", "RNG / hydrogen blending pilots and recovery", "Rate case equity layer and ROE decisions"],
    "P/E 15-18x. EV/EBITDA 9-11x. P/B 1.5-2.0x. Dividend yield 3.5-4.5%. Rate base CAGR 6-9% at best-in-class LDCs.")

_add_industry("Utilities — Multi-Utilities", "Utilities",
    "Multi-utilities operate combined electric, gas (and sometimes water) services across multiple regulatory jurisdictions. Diversification smooths rate-case risk across subsidiaries but adds complexity. Sum-of-the-parts valuation is common; the best multi-utilities out-earn allowed ROEs through operating efficiency and tight capex execution.",
    ["Rate Base Growth (weighted)", "Blended Allowed ROE", "Jurisdictional Mix Quality", "FFO / Debt", "Consolidated Dividend Coverage", "Equity Issuance Cadence"],
    ["Multi-jurisdictional rate case timing", "Holding-company leverage creep", "Equity issuance diluting per-share growth", "Subsidiary underperformance in weakest jurisdiction", "Pension / OPEB liabilities at parent"],
    ["Blended earned-vs-allowed ROE across subs", "Holding-company debt ratio", "Capex allocation by subsidiary", "Equity issuance plans vs DRIP", "Jurisdiction-by-jurisdiction rate case calendar"],
    "P/E 15-19x. EV/EBITDA 9-11x. Sum-of-parts premium for best jurisdictions. Dividend yield 3.5-4.5%. Target EPS CAGR 5-8%.")

_add_industry("Utilities — Renewable Electricity", "Utilities",
    "Renewable electricity utilities and YieldCos own wind, solar, and storage portfolios under long-term power purchase agreements (PPAs) or regulated contracts. Cash flows are predictable but capital-intensive; growth depends on the sponsor's development pipeline and the cost of incremental equity. Interest rates materially affect both project economics and dividend-paying capacity.",
    ["CAFD (Cash Available for Distribution) per Share", "PPA Coverage / Weighted Average Life", "Dividend Coverage (CAFD)", "FFO / Debt", "Contracted vs Merchant Mix", "Development Pipeline (GW)"],
    ["PPA re-contracting risk at maturity", "Interest-rate pressure on equity-funded growth", "Curtailment and congestion losses", "Resource volatility (wind / solar underperformance)", "Sponsor dropdown pricing fairness", "Tax credit (ITC / PTC) policy reversals"],
    ["Weighted-average PPA life and counterparty quality", "CAFD growth vs dividend growth targets", "Cost of equity vs project IRRs", "Dropdown pricing multiples", "Merchant tail exposure post-PPA", "Project-level leverage ratios"],
    "EV/EBITDA 10-14x. P/CAFD 12-18x. Dividend yield 4-7% with 5-8% CAGR target. IRR spread: project IRR minus cost of capital should exceed 200-300bps.")

_add_industry("Utilities — Independent Power Producers", "Utilities",
    "Independent power producers (IPPs) and merchant generators sell electricity into wholesale markets, often with partial hedging through PPAs or tolling agreements. Earnings are highly sensitive to natural gas prices, heat rates, and capacity market clearing prices. The best IPPs have long-dated hedges, low-cost generation, and disciplined capital allocation in a commoditised business.",
    ["Adjusted EBITDA / Generation Volume", "Hedge Coverage (% and Years)", "Capacity Factor", "FCF Yield", "Net Debt / EBITDA", "Heat Rate (for gas fleets)"],
    ["Power price collapse or spark-spread compression", "Capacity market design changes", "Unit outages and forced derates", "Gas price spikes (for non-hedged merchant fleets)", "ERCOT / PJM regulatory interventions", "ESG-driven fleet-retirement mandates"],
    ["Forward power curves and spark/dark spreads", "Hedge portfolio % coverage 1-3 years out", "Capacity auction results", "Operating availability and forced outage rates", "Heat-rate improvements and capex efficiency", "Fleet transition capex vs buybacks"],
    "EV/EBITDA 6-9x (lower than regulated). FCF yield 8-12%. P/E unstable due to mark-to-market derivatives. Focus on leverage and hedge mix.")

_add_industry("Utilities — Regulated Water", "Utilities",
    "Regulated water and wastewater utilities earn returns on a rate base dominated by pipes, treatment plants and storage. System modernization driven by PFAS, lead-pipe replacement and climate resilience supports multi-decade capex visibility. Tuck-in M&A of municipal systems is a material growth lever for the largest names.",
    ["Rate Base Growth", "Allowed ROE", "Acquisition Cadence (municipal M&A)", "Capex / Revenue", "FFO / Debt", "Dividend Coverage"],
    ["PFAS / lead-pipe liability and remediation costs", "Drought and water-availability stress", "Affordability / rate shock on lower-income customers", "Slow municipal M&A approval", "Environmental compliance capex overruns"],
    ["Municipal acquisition pipeline and closings", "PFAS and lead-service-line recovery mechanisms", "Capex visibility (5-10 year plans)", "Allowed ROE decisions in key states", "Drought impact on volumes and fire-protection revenue"],
    "P/E 20-28x (premium to electric on duration). EV/EBITDA 13-17x. P/B 2.5-3.5x. Dividend yield 2-3%. Rate base CAGR 7-10%.")

_add_industry("Utilities — Diversified", "Utilities",
    "Diversified utilities combine regulated and unregulated businesses: regulated T&D, midstream / LNG exposure, renewable development platforms and, at times, international operations. Sum-of-the-parts analysis is essential. Capital allocation between regulated growth and competitive platforms drives returns.",
    ["Sum-of-Parts Fair Value", "Earnings Mix (Regulated vs Competitive)", "Consolidated FFO / Debt", "Regulated Rate Base Growth", "Unregulated Segment Returns"],
    ["Holding-company leverage masking subsidiary health", "Competitive-segment volatility", "International / FX exposure", "Capital misallocation between regulated and unregulated", "Credit rating actions at holdco level"],
    ["Segment earnings splits and multi-year guidance", "Capex allocation between regulated and competitive", "Divestitures of non-core assets", "Regulatory calendars across all jurisdictions", "Leverage reduction trajectory"],
    "Blended P/E 14-18x. Sum-of-parts valuation preferred. EV/EBITDA 9-12x consolidated. Dividend yield 3-4.5%. Apply 10-20% holdco conglomerate discount.")

def get_sector_insight(sector: str | None) -> SectorInsight | None:
    return _SECTORS.get(sector.lower()) if sector else None

def get_industry_insight(industry: str | None) -> IndustryInsight | None:
    return _INDUSTRIES.get(industry.lower()) if industry else None

def list_sectors() -> list[str]:
    return sorted(s.sector for s in _SECTORS.values())

def list_industries() -> list[str]:
    return sorted(i.industry for i in _INDUSTRIES.values())
