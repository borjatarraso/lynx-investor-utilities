"""Metric explanations for Lynx Energy Analysis."""

from __future__ import annotations
from lynx_energy.models import MetricExplanation

METRIC_EXPLANATIONS: dict[str, MetricExplanation] = {}

def _add(key, full_name, description, why_used, formula, category):
    METRIC_EXPLANATIONS[key] = MetricExplanation(key=key, full_name=full_name, description=description,
                                                  why_used=why_used, formula=formula, category=category)

# Valuation
_add("pe_trailing", "Price-to-Earnings Ratio (TTM)", "Compares stock price to trailing 12-month earnings per share.", "Most widely used valuation metric. Low P/E may indicate undervaluation.", "P/E = Price / EPS (TTM)", "valuation")
_add("pb_ratio", "Price-to-Book Ratio", "Compares stock price to book value per share.", "Core metric for value investing. P/B < 1 means trading below liquidation value.", "P/B = Price / Book Value per Share", "valuation")
_add("ps_ratio", "Price-to-Sales Ratio", "Compares stock price to revenue per share.", "Useful for pre-profit companies. P/S < 1 is generally cheap.", "P/S = Market Cap / Revenue", "valuation")
_add("p_fcf", "Price-to-Free Cash Flow", "Compares market cap to free cash flow.", "More reliable than P/E — cash flow is harder to manipulate. Critical for energy producers.", "P/FCF = Market Cap / Free Cash Flow", "valuation")
_add("ev_ebitda", "Enterprise Value / EBITDA", "Capital-structure-neutral valuation.", "EV/EBITDA 4-8 is typical for energy producers. Preferred over P/E for cross-company comparison.", "EV/EBITDA = (Market Cap + Debt - Cash) / EBITDA", "valuation")
_add("ev_revenue", "Enterprise Value / Revenue", "Compares enterprise value to revenue.", "Useful for pre-profit producers. EV/Revenue < 1 is very cheap.", "EV/Revenue = EV / Revenue", "valuation")
_add("peg_ratio", "PEG Ratio", "P/E adjusted by growth rate.", "PEG < 1 suggests undervalued relative to growth. Less relevant for cyclical energy companies.", "PEG = P/E / Annual EPS Growth Rate", "valuation")
_add("dividend_yield", "Dividend Yield", "Annual dividend as percentage of price.", "Common for large energy producers and midstream companies. Junior E&P rarely pays dividends.", "Yield = Annual Dividends / Price", "valuation")
_add("earnings_yield", "Earnings Yield", "Inverse of P/E ratio.", "Compare to bond yields for relative attractiveness.", "Earnings Yield = EPS / Price", "valuation")
_add("price_to_tangible_book", "Price / Tangible Book", "Price vs tangible book value per share.", "More conservative than P/B. Critical for asset-heavy energy companies.", "P/TBV = Price / (Equity - Intangibles) / Shares", "valuation")
_add("price_to_ncav", "Price / NCAV (Net-Net)", "Price vs net current asset value per share.", "Graham's net-net criterion. Below NCAV = trading below liquidation value.", "P/NCAV = Price / (Current Assets - Total Liabilities) / Shares", "valuation")
_add("cash_to_market_cap", "Cash-to-Market-Cap Ratio", "How much of market cap is backed by cash.", "Critical for explorers. >50% means buying exploration assets cheaply or even for free. >30% is strong cash backing.", "Cash / Market Cap = Total Cash / Market Capitalization", "valuation")
_add("ev_per_boe", "EV per BOE of Reserves", "Enterprise value per barrel of oil equivalent of proved reserves.", "Key metric for oil & gas E&P. Compare within same basin and reserve category. Lower EV/BOE = cheaper reserves.", "EV / Total Proved Reserves (BOE)", "valuation")
_add("ev_per_mcfe", "EV per MCFE of Reserves", "Enterprise value per thousand cubic feet equivalent of reserves.", "Key metric for natural gas focused E&P. Compare only within same commodity and stage.", "EV / Total Reserves (MCFE)", "valuation")
_add("p_nav", "Price / Net Asset Value", "Market cap vs NAV from reserve reports or economic studies.", "Primary valuation for development/production energy companies. PDP NAV is the floor, 2P NAV represents upside.", "P/NAV = Market Cap / NPV from Reserve Report", "valuation")

# Profitability
_add("roe", "Return on Equity", "Profit generated per dollar of equity.", "Target ROE > 15% for producers. Less meaningful for pre-revenue explorers.", "ROE = Net Income / Equity", "profitability")
_add("roa", "Return on Assets", "Profit per dollar of assets.", "ROA > 5% is good. Not inflated by leverage.", "ROA = Net Income / Total Assets", "profitability")
_add("roic", "Return on Invested Capital", "Return on all invested capital.", "ROIC > 10% suggests competitive advantage. Key for energy producers.", "ROIC = NOPAT / Invested Capital", "profitability")
_add("gross_margin", "Gross Margin", "Revenue remaining after cost of goods sold.", "For energy producers, indicates cost efficiency. High margins = low-cost producer with favorable breakeven.", "Gross Margin = Gross Profit / Revenue", "profitability")
_add("operating_margin", "Operating Margin", "Revenue remaining after all operating expenses.", "Shows core business profitability. Relevant for producers only.", "Operating Margin = Operating Income / Revenue", "profitability")
_add("net_margin", "Net Profit Margin", "Revenue remaining as net profit.", "Bottom line profitability. Not applicable for pre-revenue energy explorers.", "Net Margin = Net Income / Revenue", "profitability")
_add("fcf_margin", "Free Cash Flow Margin", "Revenue converted to free cash flow.", "Measures actual cash generation. Critical for energy producers — shows capital discipline.", "FCF Margin = FCF / Revenue", "profitability")
_add("ebitda_margin", "EBITDA Margin", "Revenue remaining as EBITDA.", "Approximates operating cash flow. EBITDA Margin > 30% is excellent for energy.", "EBITDA Margin = EBITDA / Revenue", "profitability")

# Solvency
_add("debt_to_equity", "Debt-to-Equity Ratio", "Debt financing vs equity financing.", "Junior explorers should have near-zero debt. Any debt in pre-revenue is a red flag. Producers can sustain higher leverage.", "D/E = Total Debt / Equity", "solvency")
_add("current_ratio", "Current Ratio", "Short-term asset coverage of liabilities.", "CR > 2 is healthy. < 1.0 signals near-term liquidity risk.", "Current Ratio = Current Assets / Current Liabilities", "solvency")
_add("quick_ratio", "Quick Ratio", "Liquidity excluding inventory.", "More conservative than current ratio.", "Quick Ratio = (Current Assets - Inventory) / Current Liabilities", "solvency")
_add("interest_coverage", "Interest Coverage", "Ability to pay interest from operating earnings.", "> 4 is comfortable. < 1.5 is dangerous. Energy companies often carry significant debt.", "Interest Coverage = Operating Income / Interest Expense", "solvency")
_add("altman_z_score", "Altman Z-Score", "Bankruptcy probability predictor.", "Z > 2.99: Safe. 1.81-2.99: Grey zone. < 1.81: Distress. Less meaningful for pre-revenue energy companies.", "Z = 1.2(WC/TA) + 1.4(RE/TA) + 3.3(EBIT/TA) + 0.6(MV/TL) + 1.0(Sales/TA)", "solvency")
_add("cash_burn_rate", "Cash Burn Rate", "Annual rate of cash consumption.", "Critical for pre-revenue energy explorers. Determines survival without financing.", "Cash Burn = Annual Operating Cash Flow (when negative)", "solvency")
_add("cash_runway_years", "Cash Runway", "Years of operation at current burn rate.", "< 1 year = imminent financing. > 3 years = comfortable. 18+ months is the target for junior E&P.", "Cash Runway = Total Cash / Annual Burn Rate", "solvency")
_add("ncav_per_share", "NCAV Per Share", "Net current asset value per share.", "Graham's net-net. If price < NCAV, trading below liquidation value.", "NCAV/Share = (Current Assets - Total Liabilities) / Shares", "solvency")
_add("burn_as_pct_of_market_cap", "Burn Rate % of Market Cap", "How fast the company consumes value.", "Below 2% quarterly is ideal. >8% annually is a red flag — the company is burning through its market cap too fast.", "Burn % = |Annual Burn Rate| / Market Cap", "solvency")

# Growth
_add("revenue_growth_yoy", "Revenue Growth (YoY)", "Annual revenue change.", "Shows business trajectory. Relevant for producers and royalty companies.", "Growth = (Rev_Current - Rev_Prior) / |Rev_Prior|", "growth")
_add("revenue_cagr_3y", "Revenue CAGR (3-Year)", "3-year compound revenue growth.", "Smooths commodity price volatility. > 10% is strong for mature energy companies.", "CAGR = (End/Start)^(1/3) - 1", "growth")
_add("earnings_growth_yoy", "Earnings Growth (YoY)", "Annual net income change.", "Drives stock appreciation for producers. Heavily influenced by commodity prices.", "Growth = (NI_Current - NI_Prior) / |NI_Prior|", "growth")
_add("shares_growth_yoy", "Share Dilution (YoY)", "Annual change in shares outstanding.", "Critical metric for junior energy companies. >10%/yr is heavy dilution destroying shareholder value. <5%/yr is acceptable.", "Dilution = (Shares_Current - Shares_Prior) / Shares_Prior", "growth")
_add("shares_growth_3y_cagr", "Dilution CAGR (3-Year)", "3-year compound share dilution rate.", "Shows persistent dilution pattern. >10%/yr CAGR is a structural problem.", "CAGR = (Shares_End / Shares_Start)^(1/3) - 1", "growth")
_add("quality_score", "Energy Quality Score", "Composite quality score (0-100).", "Evaluates insider ownership, financial position, dilution risk, asset backing, and business viability. Weights adapt by development stage. >70 is high quality, <30 is weak.", "Weighted sum of: insider alignment, financial position, dilution risk, asset backing, revenue status", "energy_quality")

# Energy-specific capital discipline & cash flow metrics
_add("fcf_yield", "FCF Yield", "Free cash flow as percentage of enterprise value.", "The best single valuation anchor for energy producers. FCF yield >10% is attractive, <5% is expensive. Preferred over P/E for cyclical companies.", "FCF Yield = Free Cash Flow / Enterprise Value", "valuation")
_add("croci", "Cash Return on Capital Invested", "Operating cash flow as return on invested capital.", "Measures actual cash returns vs accounting returns (ROIC). CROCI >12% indicates strong capital allocation. Energy-specific: avoids depreciation distortion from reserve depletion.", "CROCI = Operating Cash Flow / (Total Assets - Cash)", "profitability")
_add("ocf_to_net_income", "OCF / Net Income Ratio", "How much of reported earnings converts to actual cash.", "Earnings quality check. Ratio >1.0 means cash flow exceeds earnings (good). Ratio <0.7 suggests aggressive accounting. Energy-specific: depreciation policies vary widely.", "OCF/NI = Operating Cash Flow / |Net Income|", "profitability")
_add("debt_per_share", "Debt Per Share", "Total debt burden allocated per share.", "Shows leverage at the shareholder level. Compare to cash per share and book value. Energy companies often carry significant project debt.", "Debt/Share = Total Debt / Shares Outstanding", "solvency")
_add("debt_service_coverage", "Debt Service Coverage", "Ability to service debt from operating cash flow.", "More conservative than interest coverage — considers total debt service. >4x is comfortable, <2x is tight, <1x cannot cover debt from operations.", "DSC = Operating Cash Flow / Interest Expense", "solvency")
_add("capex_to_revenue", "Capex / Revenue", "Capital expenditure as percentage of revenue.", "Shows capital intensity. Energy E&P: 20-35% typical. >50% indicates aggressive growth or declining production requiring heavy reinvestment. <15% may signal under-investment.", "Capex % = |Capital Expenditure| / Revenue", "growth")
_add("capex_to_ocf", "Capex / Operating Cash Flow", "Capital spending relative to cash generation.", "Critical for energy producers. >80% leaves little FCF for dividends/buybacks. <40% indicates harvesting mode. Sustainable long-term range: 40-60%.", "Capex/OCF = |Capital Expenditure| / Operating Cash Flow", "growth")
_add("reinvestment_rate", "Reinvestment Rate", "Capital expenditure as percentage of EBITDA.", "Shows how much operating profit is reinvested. >70% = growth phase. 30-50% = balanced. <30% = harvesting. Energy companies must reinvest to offset production decline.", "Reinvestment = |Capex| / EBITDA", "growth")
_add("dividend_payout_ratio", "Dividend Payout Ratio", "Percentage of net income paid as dividends.", ">80% is unsustainable for cyclical energy. 30-60% is healthy. Energy majors target 40-50% payout with buyback flexibility.", "Payout = |Dividends| / Net Income", "growth")
_add("dividend_coverage", "Dividend Coverage (FCF)", "How many times FCF covers the dividend.", "Most important dividend safety metric. >2x is safe, 1.0-1.5x is tight, <1x means dividend exceeds FCF (cut risk). Energy-specific: cyclical FCF makes this volatile.", "Coverage = Free Cash Flow / |Dividends Paid|", "growth")
_add("shareholder_yield", "Shareholder Yield", "Total cash returned to shareholders as percentage of market cap.", "Combines dividends + buybacks. >8% is exceptional for energy. Preferred over dividend yield alone because energy majors increasingly use buybacks.", "Yield = (Dividends + Buybacks) / Market Cap", "growth")
_add("fcf_per_share", "FCF Per Share", "Free cash flow allocated per share.", "Per-share cash generation. Track trend over multiple years. Rising FCF/share is the best indicator of improving capital efficiency.", "FCF/Share = Free Cash Flow / Shares Outstanding", "growth")
_add("ocf_per_share", "OCF Per Share", "Operating cash flow allocated per share.", "Less capex-dependent than FCF/share. Shows base cash-generating power before capital allocation decisions.", "OCF/Share = Operating Cash Flow / Shares Outstanding", "growth")
_add("fcf_conversion", "FCF / EBITDA Conversion", "How efficiently EBITDA converts to free cash flow.", ">50% is excellent. 30-50% is typical for energy. <20% indicates heavy capex or working capital consumption.", "FCF Conversion = Free Cash Flow / EBITDA", "efficiency")
_add("capex_intensity", "Capex Intensity", "Capital expenditure as share of revenue.", "Same as capex/revenue but tracked in efficiency context. Energy sector has inherently high capex intensity (15-40%). Compare within sub-sector.", "Intensity = |Capex| / Revenue", "efficiency")

SECTION_EXPLANATIONS = {
    "profile": {"title": "Company Profile", "description": "Company identification, market cap tier, energy development stage, primary commodity, and jurisdiction risk classification."},
    "valuation": {"title": "Valuation Metrics", "description": "Price-based ratios including traditional metrics and energy-specific valuations (cash-to-market-cap, EV/BOE). For pre-revenue explorers, cash backing replaces P/E as the primary metric."},
    "profitability": {"title": "Profitability Metrics", "description": "Margin and return analysis. Not applicable for pre-revenue explorers. For producers, netback and operating margins indicate cost efficiency vs commodity price."},
    "solvency": {"title": "Solvency & Survival", "description": "Balance sheet strength, liquidity, and survival metrics. Cash burn rate and runway are critical for junior E&P. Explorers should have minimal debt. 18+ months cash runway is the target."},
    "growth": {"title": "Growth & Dilution", "description": "Revenue/earnings growth for producers, and share dilution tracking for all stages. Dilution is the #1 risk for junior energy companies — heavy dilution (>10%/yr) destroys shareholder value."},
    "share_structure": {"title": "Share Structure", "description": "Analysis of outstanding shares, fully diluted count, insider ownership, and institutional holdings. Tight structure (<150M shares) with high insider ownership (>10%) is ideal."},
    "energy_quality": {"title": "Energy Quality Assessment", "description": "Stage-appropriate quality scoring. Evaluates insider alignment, financial position, dilution risk, asset backing, and revenue status. Replaces traditional moat analysis with energy-specific factors."},
    "intrinsic_value": {"title": "Intrinsic Value Estimates", "description": "Multiple valuation methods adapted by stage. Producers: DCF/EV/EBITDA. Developers: P/NAV from field development economics. Explorers: EV/BOE and asset-based. Early exploration: cash backing."},
    "conclusion": {"title": "Assessment Conclusion", "description": "Weighted scoring across 5 categories with weights adapted by both tier and stage. Includes a screening checklist evaluating key quality criteria for energy companies."},
}

CONCLUSION_METHODOLOGY = {
    "overall": {"title": "Conclusion Methodology", "description": "Score is a weighted average of 5 categories (valuation, profitability, solvency, growth, energy quality). Weights vary by BOTH company tier AND development stage. Explorers weight solvency at 35-40% and energy quality at 30-35%. Producers use more balanced weights. Verdicts: Strong Buy (>=75), Buy (>=60), Hold (>=45), Caution (>=30), Avoid (<30)."},
    "valuation": {"title": "Valuation Score", "description": "Starts at 50. Adjusted by P/E, P/B, cash-to-market-cap (bonus for explorers), and EV/EBITDA. Pre-revenue metrics are excluded for explorer/grassroots stages."},
    "solvency": {"title": "Solvency Score", "description": "Starts at 50. Debt/equity, current ratio, cash runway, and burn rate as % of market cap. Explorers are penalized heavily for any debt. Cash runway < 1 year = -25 points."},
    "energy_quality": {"title": "Energy Quality Score", "description": "Composite of insider alignment (20pts), financial position (25pts), dilution risk (20pts), asset backing (20pts), and revenue/stage status (15pts). Share structure bonus/penalty."},
}

def get_explanation(key): return METRIC_EXPLANATIONS.get(key)
def get_section_explanation(section): return SECTION_EXPLANATIONS.get(section)
def get_conclusion_explanation(category=None): return CONCLUSION_METHODOLOGY.get(category or "overall")
def list_metrics(category=None):
    metrics = list(METRIC_EXPLANATIONS.values())
    return [m for m in metrics if m.category == category] if category else metrics
