"""Utilities-specialized metrics calculation engine.

All calculations are both tier-aware AND stage-aware. Metrics are calibrated
to regulated electric, gas, water, and multi-utility operators as well as
independent power producers and YieldCos.
"""

from __future__ import annotations

import math
from typing import Optional

from datetime import datetime, timedelta

import yfinance as yf

from lynx_utilities.models import (
    Commodity, CompanyStage, CompanyTier, EfficiencyMetrics, FinancialStatement,
    GrowthMetrics, InsiderTransaction, IntrinsicValue, MarketIntelligence,
    EnergyQualityIndicators, ProfitabilityMetrics, ShareStructure,
    SolvencyMetrics, ValuationMetrics,
)


def calc_valuation(
    info: dict, statements: list[FinancialStatement],
    tier: CompanyTier, stage: CompanyStage,
) -> ValuationMetrics:
    v = ValuationMetrics()
    v.pe_trailing = info.get("trailingPE")
    v.pe_forward = info.get("forwardPE")
    v.pb_ratio = info.get("priceToBook")
    v.ps_ratio = info.get("priceToSalesTrailing12Months")
    v.peg_ratio = info.get("pegRatio")
    v.ev_ebitda = info.get("enterpriseToEbitda")
    v.ev_revenue = info.get("enterpriseToRevenue")
    v.dividend_yield = info.get("trailingAnnualDividendYield") or info.get("dividendYield")
    v.enterprise_value = info.get("enterpriseValue")
    v.market_cap = info.get("marketCap")

    if v.pe_trailing and v.pe_trailing > 0:
        v.earnings_yield = 1.0 / v.pe_trailing

    price = info.get("currentPrice") or info.get("regularMarketPrice")
    shares = info.get("sharesOutstanding")

    if price and shares and statements:
        latest = statements[0]
        if latest.free_cash_flow and latest.free_cash_flow > 0:
            v.p_fcf = (price * shares) / latest.free_cash_flow

    if tier in (CompanyTier.MICRO, CompanyTier.NANO, CompanyTier.SMALL, CompanyTier.MID) and statements:
        latest = statements[0]
        if latest.total_equity and latest.total_assets and price and shares:
            tbv = latest.total_equity
            if shares > 0:
                tbv_per_share = tbv / shares
                if tbv_per_share > 0:
                    v.price_to_tangible_book = price / tbv_per_share
        if latest.current_assets and latest.total_liabilities and shares and shares > 0:
            ncav = latest.current_assets - latest.total_liabilities
            ncav_ps = ncav / shares
            if ncav_ps > 0 and price:
                v.price_to_ncav = price / ncav_ps

    total_cash = info.get("totalCash")
    if total_cash and v.market_cap and v.market_cap > 0:
        v.cash_to_market_cap = total_cash / v.market_cap

    # FCF Yield (FCF / Enterprise Value)
    if statements and v.enterprise_value and v.enterprise_value > 0:
        latest = statements[0]
        if latest.free_cash_flow is not None:
            v.fcf_yield = latest.free_cash_flow / v.enterprise_value

    return v


def calc_profitability(
    info: dict, statements: list[FinancialStatement],
    tier: CompanyTier, stage: CompanyStage,
) -> ProfitabilityMetrics:
    p = ProfitabilityMetrics()
    p.roe = info.get("returnOnEquity")
    p.roa = info.get("returnOnAssets")
    p.gross_margin = info.get("grossMargins")
    p.operating_margin = info.get("operatingMargins")
    p.net_margin = info.get("profitMargins")

    if statements:
        s = statements[0]
        if s.operating_income is not None and s.total_assets and s.total_cash is not None:
            nopat = s.operating_income * 0.75
            invested_capital = s.total_assets - (s.total_cash or 0)
            if invested_capital > 0:
                p.roic = nopat / invested_capital
        if s.free_cash_flow and s.revenue and s.revenue > 0:
            p.fcf_margin = s.free_cash_flow / s.revenue
        if s.ebitda and s.revenue and s.revenue > 0:
            p.ebitda_margin = s.ebitda / s.revenue

        # CROCI — Cash Return on Capital Invested
        if s.operating_cash_flow and s.total_assets and s.total_cash is not None:
            invested = s.total_assets - (s.total_cash or 0)
            if invested > 0:
                p.croci = s.operating_cash_flow / invested

        # Operating Cash Flow to Net Income ratio (earnings quality)
        if s.operating_cash_flow and s.net_income and s.net_income > 0:
            p.ocf_to_net_income = s.operating_cash_flow / s.net_income

    return p


def calc_solvency(
    info: dict, statements: list[FinancialStatement],
    tier: CompanyTier, stage: CompanyStage,
) -> SolvencyMetrics:
    s = SolvencyMetrics()
    s.debt_to_equity = info.get("debtToEquity")
    if s.debt_to_equity:
        s.debt_to_equity /= 100
    s.current_ratio = info.get("currentRatio")
    s.quick_ratio = info.get("quickRatio")
    s.total_debt = info.get("totalDebt")
    s.total_cash = info.get("totalCash")

    if s.total_debt is not None and s.total_cash is not None:
        s.net_debt = s.total_debt - s.total_cash

    shares = info.get("sharesOutstanding")
    market_cap = info.get("marketCap")

    if statements:
        st = statements[0]

        if st.ebitda and st.ebitda > 0 and s.total_debt:
            s.debt_to_ebitda = s.total_debt / st.ebitda

        if st.operating_income:
            ie = abs(st.interest_expense) if st.interest_expense else None
            if ie is None and s.total_debt:
                ie = s.total_debt * 0.05
            if ie and ie > 0:
                s.interest_coverage = st.operating_income / ie

        if st.total_assets and st.total_assets > 0 and st.revenue and st.revenue > 0:
            ta = st.total_assets
            wc = 0
            if st.current_assets is not None and st.current_liabilities is not None:
                wc = st.current_assets - st.current_liabilities
            re = (st.total_equity or 0) * 0.5
            ebit = st.operating_income or 0
            mcap = info.get("marketCap", 0)
            tl = st.total_liabilities or 0
            if tl <= 0:
                s.altman_z_score = None
            else:
                rev = st.revenue or 0
                z = (1.2 * wc / ta + 1.4 * re / ta + 3.3 * ebit / ta +
                     0.6 * mcap / tl + 1.0 * rev / ta)
                s.altman_z_score = round(z, 2)

        if st.current_assets is not None and st.current_liabilities is not None:
            s.working_capital = st.current_assets - st.current_liabilities

        if s.total_cash and shares and shares > 0:
            s.cash_per_share = s.total_cash / shares

        if st.total_equity:
            s.tangible_book_value = st.total_equity

        if st.current_assets is not None and st.total_liabilities is not None:
            s.ncav = st.current_assets - st.total_liabilities
            if shares and shares > 0:
                s.ncav_per_share = s.ncav / shares

        if st.operating_cash_flow is not None:
            ocf = st.operating_cash_flow
            if ocf < 0:
                s.cash_burn_rate = ocf
                if s.total_cash and s.total_cash > 0:
                    s.cash_runway_years = s.total_cash / abs(ocf)
                s.quarterly_burn_rate = ocf / 4
            else:
                s.cash_burn_rate = 0

        if s.cash_burn_rate and s.cash_burn_rate < 0 and market_cap and market_cap > 0:
            s.burn_as_pct_of_market_cap = abs(s.cash_burn_rate) / market_cap

    # Debt per share and net debt per share
    if shares:
        if s.total_debt is not None and shares > 0:
            s.debt_per_share = s.total_debt / shares
        if s.net_debt is not None and shares > 0:
            s.net_debt_per_share = s.net_debt / shares

    # Debt service coverage (OCF / total debt service)
    if statements and s.total_debt and s.total_debt > 0:
        st = statements[0]
        if st.operating_cash_flow and st.operating_cash_flow > 0:
            ie = abs(st.interest_expense) if st.interest_expense else s.total_debt * 0.05
            s.debt_service_coverage = st.operating_cash_flow / ie if ie > 0 else None

    return s


def calc_growth(
    statements: list[FinancialStatement],
    tier: CompanyTier, stage: CompanyStage,
) -> GrowthMetrics:
    g = GrowthMetrics()
    if len(statements) < 2:
        return g
    stmts = statements

    if stmts[0].revenue and stmts[1].revenue and stmts[1].revenue != 0:
        g.revenue_growth_yoy = (stmts[0].revenue - stmts[1].revenue) / abs(stmts[1].revenue)

    if stmts[0].net_income and stmts[1].net_income and stmts[1].net_income != 0:
        g.earnings_growth_yoy = (stmts[0].net_income - stmts[1].net_income) / abs(stmts[1].net_income)

    if stmts[0].free_cash_flow and stmts[1].free_cash_flow and stmts[1].free_cash_flow != 0:
        g.fcf_growth_yoy = (stmts[0].free_cash_flow - stmts[1].free_cash_flow) / abs(stmts[1].free_cash_flow)

    if stmts[0].book_value_per_share and stmts[1].book_value_per_share and stmts[1].book_value_per_share != 0:
        g.book_value_growth_yoy = (stmts[0].book_value_per_share - stmts[1].book_value_per_share) / abs(stmts[1].book_value_per_share)

    if stmts[0].shares_outstanding and stmts[1].shares_outstanding and stmts[1].shares_outstanding > 0:
        g.shares_growth_yoy = (stmts[0].shares_outstanding - stmts[1].shares_outstanding) / stmts[1].shares_outstanding

    if len(stmts) >= 4 and stmts[0].shares_outstanding and stmts[3].shares_outstanding:
        g.shares_growth_3y_cagr = _cagr(stmts[3].shares_outstanding, stmts[0].shares_outstanding, 3)

    if len(stmts) >= 4:
        g.revenue_cagr_3y = _cagr(stmts[3].revenue, stmts[0].revenue, 3)
        g.earnings_cagr_3y = _cagr(stmts[3].net_income, stmts[0].net_income, 3)

    if len(stmts) >= 5:
        g.revenue_cagr_5y = _cagr(stmts[-1].revenue, stmts[0].revenue, len(stmts) - 1)
        g.earnings_cagr_5y = _cagr(stmts[-1].net_income, stmts[0].net_income, len(stmts) - 1)

    # Utilities capital discipline metrics
    if stmts[0].capital_expenditure is not None:
        capex = abs(stmts[0].capital_expenditure)

        if stmts[0].revenue and stmts[0].revenue > 0:
            g.capex_to_revenue = capex / stmts[0].revenue

        if stmts[0].operating_cash_flow and stmts[0].operating_cash_flow > 0:
            g.capex_to_ocf = capex / stmts[0].operating_cash_flow

        if stmts[0].ebitda and stmts[0].ebitda > 0:
            g.reinvestment_rate = capex / stmts[0].ebitda

    # Dividend analysis
    if stmts[0].dividends_paid and stmts[0].net_income and stmts[0].net_income > 0:
        g.dividend_payout_ratio = abs(stmts[0].dividends_paid) / stmts[0].net_income

    if stmts[0].dividends_paid and stmts[0].free_cash_flow and stmts[0].free_cash_flow > 0:
        g.dividend_coverage = stmts[0].free_cash_flow / abs(stmts[0].dividends_paid)

    # Per-share metrics
    shares = stmts[0].shares_outstanding
    if shares and shares > 0:
        if stmts[0].free_cash_flow is not None:
            g.fcf_per_share = stmts[0].free_cash_flow / shares
        if stmts[0].operating_cash_flow is not None:
            g.ocf_per_share = stmts[0].operating_cash_flow / shares

    return g


def calc_efficiency(
    info: dict, statements: list[FinancialStatement], tier: CompanyTier,
) -> EfficiencyMetrics:
    e = EfficiencyMetrics()
    if not statements:
        return e
    s = statements[0]
    if s.revenue and s.total_assets and s.total_assets > 0:
        e.asset_turnover = s.revenue / s.total_assets

    # FCF conversion (FCF / EBITDA)
    if s.free_cash_flow is not None and s.ebitda and s.ebitda > 0:
        e.fcf_conversion = s.free_cash_flow / s.ebitda

    # Capex intensity (Capex / Revenue)
    if s.capital_expenditure is not None and s.revenue and s.revenue > 0:
        e.capex_intensity = abs(s.capital_expenditure) / s.revenue

    return e


def calc_share_structure(
    info: dict, statements: list[FinancialStatement],
    growth: GrowthMetrics, tier: CompanyTier, stage: CompanyStage,
) -> ShareStructure:
    ss = ShareStructure()
    ss.shares_outstanding = info.get("sharesOutstanding")
    ss.float_shares = info.get("floatShares")
    ss.insider_ownership_pct = info.get("heldPercentInsiders")
    ss.institutional_ownership_pct = info.get("heldPercentInstitutions")

    implied = info.get("impliedSharesOutstanding")
    if implied:
        ss.fully_diluted_shares = implied
    elif ss.shares_outstanding:
        ss.fully_diluted_shares = ss.shares_outstanding

    if ss.shares_outstanding and ss.fully_diluted_shares and ss.shares_outstanding > 0:
        ratio = ss.fully_diluted_shares / ss.shares_outstanding
        if growth:
            growth.dilution_ratio = ratio
            growth.fully_diluted_shares = ss.fully_diluted_shares

    if ss.fully_diluted_shares:
        fd = ss.fully_diluted_shares
        if fd < 80_000_000:
            ss.share_structure_assessment = "Very Tight (<80M shares)"
        elif fd < 150_000_000:
            ss.share_structure_assessment = "Tight (80-150M shares)"
        elif fd < 300_000_000:
            ss.share_structure_assessment = "Moderate (150-300M shares)"
        elif fd < 500_000_000:
            ss.share_structure_assessment = "Heavy (300-500M shares)"
        else:
            ss.share_structure_assessment = "Bloated (>500M shares)"

    return ss


def calc_energy_quality(
    profitability: ProfitabilityMetrics,
    growth: GrowthMetrics,
    solvency: SolvencyMetrics,
    share_structure: ShareStructure,
    statements: list[FinancialStatement],
    info: dict,
    tier: CompanyTier,
    stage: CompanyStage,
) -> EnergyQualityIndicators:
    m = EnergyQualityIndicators()
    score = 0.0
    max_score = 0.0

    # Insider Ownership (20 pts)
    max_score += 20
    insider_pct = share_structure.insider_ownership_pct if share_structure else None
    if insider_pct is not None:
        if insider_pct > 0.20:
            m.insider_alignment = "Strong alignment — >20% insider ownership"
            m.management_quality = "Significant skin in the game"
            score += 20
        elif insider_pct > 0.10:
            m.insider_alignment = "Good alignment — 10-20% insider ownership"
            m.management_quality = "Meaningful insider stake"
            score += 14
        elif insider_pct > 0.05:
            m.insider_alignment = "Moderate — 5-10% insider ownership"
            m.management_quality = "Some insider participation"
            score += 8
        else:
            m.insider_alignment = "Low insider ownership (<5%)"
            m.management_quality = "Limited management alignment"
            score += 2
        m.insider_ownership_pct = insider_pct
    else:
        m.insider_alignment = "Insider data unavailable"
        score += 5

    # Financial Position (25 pts)
    max_score += 25
    if solvency.cash_runway_years is not None:
        if solvency.cash_runway_years > 3:
            m.financial_position = "Strong — >3 years runway"
            score += 25
        elif solvency.cash_runway_years > 1.5:
            m.financial_position = "Adequate — 1.5-3 years runway"
            score += 16
        elif solvency.cash_runway_years > 0.75:
            m.financial_position = "Tight — financing likely needed within 12 months"
            score += 6
        else:
            m.financial_position = "Critical — near-term financing required"
    elif solvency.cash_burn_rate is not None and solvency.cash_burn_rate >= 0:
        m.financial_position = "Cash flow positive — no burn"
        score += 25
    else:
        m.financial_position = "Insufficient data"
        score += 10

    # Dilution Risk (20 pts)
    max_score += 20
    dil = growth.shares_growth_yoy if growth else None
    if dil is not None:
        if dil < 0.01:
            m.dilution_risk = "Minimal dilution (<1%/yr)"
            score += 20
        elif dil < 0.05:
            m.dilution_risk = "Modest dilution (1-5%/yr)"
            score += 14
        elif dil < 0.10:
            m.dilution_risk = "Moderate dilution (5-10%/yr) — monitor closely"
            score += 6
        elif dil < 0.20:
            m.dilution_risk = "Heavy dilution (10-20%/yr) — value destruction risk"
            score += 2
        else:
            m.dilution_risk = "Extreme dilution (>20%/yr) — severe warning"
    else:
        m.dilution_risk = "Dilution data unavailable"
        score += 8

    if share_structure and share_structure.share_structure_assessment:
        m.share_structure_assessment = share_structure.share_structure_assessment
        if "Tight" in share_structure.share_structure_assessment:
            score += 3
        elif "Bloated" in share_structure.share_structure_assessment:
            score -= 3

    # Asset Backing (20 pts)
    max_score += 20
    if solvency.ncav and solvency.ncav > 0:
        price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        shares = info.get("sharesOutstanding", 0)
        if price and shares and shares > 0:
            ncav_ps = solvency.ncav / shares
            if price < ncav_ps:
                m.asset_backing = "Trading below NCAV — strong asset backing"
                score += 20
            elif price < ncav_ps * 1.5:
                m.asset_backing = "Near NCAV territory"
                score += 12
            else:
                m.asset_backing = "Above NCAV but asset-backed"
                score += 5
    elif solvency.tangible_book_value and solvency.tangible_book_value > 0:
        shares = info.get("sharesOutstanding", 0)
        price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        if price and shares and shares > 0:
            tbv_ps = solvency.tangible_book_value / shares
            if price < tbv_ps:
                m.asset_backing = "Below tangible book value"
                score += 14
            elif price < tbv_ps * 1.5:
                m.asset_backing = "Near tangible book value"
                score += 8
            else:
                m.asset_backing = "Above tangible book"
                score += 3
    else:
        m.asset_backing = "Insufficient asset data"

    # Revenue / Stage (15 pts)
    max_score += 15
    revenues = [s.revenue for s in statements if s.revenue and s.revenue > 0]
    if revenues and stage == CompanyStage.PRODUCER:
        if len(revenues) >= 2 and revenues[0] > revenues[1]:
            m.revenue_predictability = "Operating utility with growing top line"
            score += 15
        else:
            m.revenue_predictability = "Operating utility with stable revenue"
            score += 10
    elif stage in (CompanyStage.EXPLORER, CompanyStage.DEVELOPER):
        m.revenue_predictability = f"{stage.value} — pre-commercial operations"
        score += 5
    elif stage == CompanyStage.GRASSROOTS:
        m.revenue_predictability = "Early-stage developer — no operating revenue expected"
        score += 2
    elif stage == CompanyStage.ROYALTY:
        m.revenue_predictability = "Contracted / YieldCo cash flows" if revenues else "Early-stage YieldCo"
        score += 15 if revenues else 5

    m.roic_history = _calc_roic_history(statements)
    m.gross_margin_history = _calc_margin_history(statements)

    m.quality_score = round((score / max_score) * 100, 1) if max_score > 0 else 0
    if m.quality_score >= 70:
        m.competitive_position = "Strong Position — High Quality"
    elif m.quality_score >= 50:
        m.competitive_position = "Viable Position — Moderate Quality"
    elif m.quality_score >= 30:
        m.competitive_position = "Speculative — Below Average Quality"
    else:
        m.competitive_position = "High Risk — Weak Fundamentals"

    return m


def calc_intrinsic_value(
    info: dict, statements: list[FinancialStatement],
    growth: GrowthMetrics, solvency: SolvencyMetrics,
    tier: CompanyTier, stage: CompanyStage,
    discount_rate: float = 0.10, terminal_growth: float = 0.03,
) -> IntrinsicValue:
    iv = IntrinsicValue()
    iv.current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    shares = info.get("sharesOutstanding")

    # Set method selection based on stage (always, even without statements)
    if stage == CompanyStage.PRODUCER:
        if tier in (CompanyTier.LARGE, CompanyTier.MID, CompanyTier.MEGA):
            iv.primary_method = "DDM / DCF"
            iv.secondary_method = "P/Rate Base & EV/EBITDA Comps"
        else:
            iv.primary_method = "P/Rate Base (P/B proxy)"
            iv.secondary_method = "DCF"
    elif stage == CompanyStage.DEVELOPER:
        iv.primary_method = "P/NAV (contracted pipeline)"
        iv.secondary_method = "Asset-Based (Tangible Book)"
    elif stage == CompanyStage.EXPLORER:
        iv.primary_method = "EV / Pipeline GW"
        iv.secondary_method = "Asset-Based (Tangible Book)"
    elif stage == CompanyStage.ROYALTY:
        iv.primary_method = "DDM / CAFD Multiple"
        iv.secondary_method = "P/NAV of Contracted Assets"
    else:
        iv.primary_method = "Cash Backing"
        iv.secondary_method = "Peer Market Cap Comparison"

    if not statements:
        return iv
    latest = statements[0]

    if stage in (CompanyStage.PRODUCER, CompanyStage.ROYALTY):
        if latest.free_cash_flow and latest.free_cash_flow > 0 and shares and shares > 0:
            fcf = latest.free_cash_flow
            growth_rate = min(growth.revenue_cagr_3y or 0.05, 0.20)
            growth_rate = max(growth_rate, 0.0)
            dr = discount_rate
            if tier == CompanyTier.SMALL:
                dr = 0.12
            elif tier in (CompanyTier.MICRO, CompanyTier.NANO):
                dr = 0.15
            if dr > terminal_growth:
                total_pv = 0.0
                projected_fcf = fcf
                for year in range(1, 11):
                    yr_growth = growth_rate - (growth_rate - terminal_growth) * (year / 10)
                    projected_fcf *= (1 + yr_growth)
                    total_pv += projected_fcf / ((1 + dr) ** year)
                terminal_fcf = projected_fcf * (1 + terminal_growth)
                terminal_value = terminal_fcf / (dr - terminal_growth)
                pv_terminal = terminal_value / ((1 + dr) ** 10)
                dcf = (total_pv + pv_terminal) / shares
                if not math.isnan(dcf) and not math.isinf(dcf) and dcf > 0:
                    iv.dcf_value = round(dcf, 2)

    eps = latest.eps or (latest.net_income / shares if latest.net_income and shares else None)
    bvps = latest.book_value_per_share or info.get("bookValue")
    if eps and eps > 0 and bvps and bvps > 0:
        iv.graham_number = round(math.sqrt(22.5 * eps * bvps), 2)

    if eps and eps > 0 and growth.earnings_cagr_3y and growth.earnings_cagr_3y > 0:
        eg = min(growth.earnings_cagr_3y * 100, 100)
        if eg > 0:
            result = eps * eg
            if not math.isnan(result) and not math.isinf(result):
                iv.lynch_fair_value = round(result, 2)

    if solvency.ncav_per_share is not None:
        iv.ncav_value = round(solvency.ncav_per_share, 4)

    if latest.total_equity and shares and shares > 0:
        iv.asset_based_value = round(latest.total_equity / shares, 4)

    if iv.current_price and iv.current_price > 0:
        if iv.dcf_value:
            iv.margin_of_safety_dcf = round((iv.dcf_value - iv.current_price) / iv.dcf_value, 4)
        if iv.graham_number:
            iv.margin_of_safety_graham = round((iv.graham_number - iv.current_price) / iv.graham_number, 4)
        if iv.ncav_value and iv.ncav_value > 0:
            iv.margin_of_safety_ncav = round((iv.ncav_value - iv.current_price) / iv.ncav_value, 4)
        if iv.asset_based_value and iv.asset_based_value > 0:
            iv.margin_of_safety_asset = round((iv.asset_based_value - iv.current_price) / iv.asset_based_value, 4)
        if iv.nav_per_share and iv.nav_per_share > 0:
            iv.margin_of_safety_nav = round((iv.nav_per_share - iv.current_price) / iv.nav_per_share, 4)

    return iv


def calc_market_intelligence(
    info: dict, ticker_obj, solvency: SolvencyMetrics,
    share_structure: ShareStructure, growth: GrowthMetrics,
    tier: CompanyTier, stage: CompanyStage,
) -> MarketIntelligence:
    """Aggregate market sentiment, insider activity, technicals, and risk warnings."""
    mi = MarketIntelligence()
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    shares_outstanding = info.get("sharesOutstanding")
    mi.price_current = price

    # ── 1. Insider transactions ──────────────────────────────────────
    try:
        insider_df = ticker_obj.insider_transactions
        if insider_df is not None and not insider_df.empty:
            top_rows = insider_df.head(10)
            for _, row in top_rows.iterrows():
                txn = InsiderTransaction(
                    insider=str(row.get("Insider", row.get("insider", ""))),
                    position=str(row.get("Position", row.get("position", ""))),
                    transaction_type=str(row.get("Transaction", row.get("transaction", ""))),
                    shares=row.get("Shares", row.get("shares")),
                    value=row.get("Value", row.get("value")),
                    date=str(row.get("Start Date", row.get("startDate", row.get("date", "")))),
                )
                mi.insider_transactions.append(txn)

            # Net shares in last 3 months
            cutoff = datetime.now() - timedelta(days=90)
            net_shares = 0.0
            buy_count = 0
            sell_count = 0
            for _, row in insider_df.iterrows():
                date_val = row.get("Start Date", row.get("startDate", row.get("date")))
                try:
                    if hasattr(date_val, "to_pydatetime"):
                        txn_date = date_val.to_pydatetime()
                    elif isinstance(date_val, str) and date_val:
                        txn_date = datetime.strptime(date_val[:10], "%Y-%m-%d")
                    else:
                        continue
                    if txn_date.tzinfo is not None:
                        txn_date = txn_date.replace(tzinfo=None)
                    if txn_date < cutoff:
                        continue
                except (ValueError, TypeError):
                    continue

                txn_type = str(row.get("Transaction", row.get("transaction", ""))).lower()
                shares_val = row.get("Shares", row.get("shares", 0)) or 0

                if any(kw in txn_type for kw in ("acquisition", "exercise", "purchase", "buy")):
                    net_shares += abs(shares_val)
                    buy_count += 1
                elif any(kw in txn_type for kw in ("disposition", "sale", "sell")):
                    net_shares -= abs(shares_val)
                    sell_count += 1

            mi.net_insider_shares_3m = net_shares

            if net_shares > 0 and buy_count > 3:
                mi.insider_buy_signal = "Strong insider buying"
            elif net_shares < 0:
                mi.insider_buy_signal = "Insider selling"
            else:
                mi.insider_buy_signal = "Mixed/Neutral"
    except Exception:
        mi.insider_buy_signal = "Data unavailable"

    # ── 2. Institutional holders ─────────────────────────────────────
    try:
        inst_df = ticker_obj.institutional_holders
        if inst_df is not None and not inst_df.empty:
            holder_col = "Holder" if "Holder" in inst_df.columns else (
                "holder" if "holder" in inst_df.columns else None
            )
            if holder_col:
                mi.top_holders = inst_df[holder_col].head(5).tolist()
    except Exception:
        pass
    mi.institutions_count = info.get("institutionsCount")
    mi.institutions_pct = share_structure.institutional_ownership_pct if share_structure else None

    # ── 3. Analyst consensus ─────────────────────────────────────────
    mi.target_high = info.get("targetHighPrice")
    mi.target_low = info.get("targetLowPrice")
    mi.target_mean = info.get("targetMeanPrice")
    mi.recommendation = info.get("recommendationKey")
    mi.analyst_count = info.get("numberOfAnalystOpinions")

    if mi.target_mean and price and price > 0:
        mi.target_upside_pct = (mi.target_mean - price) / price

    # ── 4. Short interest ────────────────────────────────────────────
    mi.shares_short = info.get("sharesShort")
    mi.short_pct_of_float = info.get("shortPercentOfFloat")
    mi.short_ratio_days = info.get("shortRatio")

    short_pct = (mi.short_pct_of_float or 0) * 100  # convert to % for thresholds
    short_ratio = mi.short_ratio_days or 0
    if short_pct > 15 and short_ratio > 5:
        mi.short_squeeze_risk = "High squeeze potential"
    elif short_pct > 8:
        mi.short_squeeze_risk = "Elevated short interest"
    else:
        mi.short_squeeze_risk = "Normal"

    # ── 5. Price technicals ──────────────────────────────────────────
    mi.price_52w_high = info.get("fiftyTwoWeekHigh")
    mi.price_52w_low = info.get("fiftyTwoWeekLow")
    mi.sma_50 = info.get("fiftyDayAverage")
    mi.sma_200 = info.get("twoHundredDayAverage")
    mi.beta = info.get("beta")
    mi.avg_volume = info.get("averageVolume")
    mi.volume_10d_avg = info.get("averageDailyVolume10Day")

    if price and mi.price_52w_high and mi.price_52w_high > 0:
        mi.pct_from_52w_high = (price - mi.price_52w_high) / mi.price_52w_high
    if price and mi.price_52w_low and mi.price_52w_low > 0:
        mi.pct_from_52w_low = (price - mi.price_52w_low) / mi.price_52w_low
    if price and mi.price_52w_high and mi.price_52w_low is not None:
        range_span = mi.price_52w_high - mi.price_52w_low
        if range_span > 0:
            mi.price_52w_range_position = (price - mi.price_52w_low) / range_span

    if price and mi.sma_50:
        mi.above_sma_50 = price > mi.sma_50
    if price and mi.sma_200:
        mi.above_sma_200 = price > mi.sma_200
    if mi.sma_50 and mi.sma_200:
        mi.golden_cross = mi.sma_50 > mi.sma_200

    if mi.volume_10d_avg and mi.avg_volume and mi.avg_volume > 0:
        vol_ratio = mi.volume_10d_avg / mi.avg_volume
        if vol_ratio > 1.25:
            mi.volume_trend = "Increasing"
        elif vol_ratio < 0.75:
            mi.volume_trend = "Decreasing"
        else:
            mi.volume_trend = "Stable"

    # --- Market context — utility input / benchmark pricing ---
    # For utilities, the most relevant front-of-curve reference is natural gas
    # (drives merchant power spreads and gas-utility commodity costs) and the
    # sector ETF (XLU). Water and transmission/distribution names have little
    # direct commodity exposure, so we fall back to 10-year yield context.
    _COMMODITY_TICKERS = {
        Commodity.MERCHANT_POWER: ("NG=F", "Henry Hub Natural Gas (power marginal fuel)"),
        Commodity.REGULATED_GAS: ("NG=F", "Henry Hub Natural Gas (input cost)"),
        Commodity.RENEWABLE_POWER: ("ICLN", "iShares Clean Energy (proxy)"),
        Commodity.NUCLEAR_GENERATION: ("URA", "Uranium ETF (fuel proxy)"),
        Commodity.REGULATED_ELECTRIC: ("^TNX", "10-Year Treasury Yield (rate sensitivity proxy)"),
        Commodity.MULTI_UTILITY: ("^TNX", "10-Year Treasury Yield (rate sensitivity proxy)"),
        Commodity.WATER: ("^TNX", "10-Year Treasury Yield (rate sensitivity proxy)"),
        Commodity.TRANSMISSION_DISTRIBUTION: ("^TNX", "10-Year Treasury Yield (rate sensitivity proxy)"),
        Commodity.DIVERSIFIED_UTILITY: ("^TNX", "10-Year Treasury Yield (rate sensitivity proxy)"),
    }
    _SECTOR_ETFS = {
        Commodity.REGULATED_ELECTRIC: [("XLU", "Utilities Select Sector SPDR"), ("VPU", "Vanguard Utilities ETF")],
        Commodity.REGULATED_GAS: [("XLU", "Utilities Select Sector SPDR"), ("UGI", "UGI Corp — peer proxy")],
        Commodity.MULTI_UTILITY: [("XLU", "Utilities Select Sector SPDR"), ("VPU", "Vanguard Utilities ETF")],
        Commodity.MERCHANT_POWER: [("XLU", "Utilities Select Sector SPDR"), ("FCG", "First Trust Natural Gas")],
        Commodity.RENEWABLE_POWER: [("ICLN", "iShares Global Clean Energy"), ("TAN", "Invesco Solar ETF")],
        Commodity.NUCLEAR_GENERATION: [("XLU", "Utilities Select Sector SPDR"), ("URNM", "Sprott Uranium Miners")],
        Commodity.WATER: [("PHO", "Invesco Water Resources ETF"), ("CGW", "Invesco S&P Global Water")],
        Commodity.TRANSMISSION_DISTRIBUTION: [("XLU", "Utilities Select Sector SPDR"), ("GRID", "First Trust NASDAQ Clean Edge Smart Grid")],
        Commodity.DIVERSIFIED_UTILITY: [("XLU", "Utilities Select Sector SPDR"), ("VPU", "Vanguard Utilities ETF")],
        Commodity.OTHER: [("XLU", "Utilities Select Sector SPDR"), ("VPU", "Vanguard Utilities ETF")],
    }

    # Detect commodity from the company profile
    company_commodity = Commodity.OTHER
    try:
        from lynx_utilities.models import classify_commodity
        desc = info.get("longBusinessSummary", "")
        industry = info.get("industry", "")
        company_commodity = classify_commodity(desc, industry)
    except Exception:
        pass

    # Fetch commodity price
    try:
        commodity_pair = _COMMODITY_TICKERS.get(company_commodity)
        if commodity_pair:
            ct = yf.Ticker(commodity_pair[0])
            ci = ct.info or {}
            mi.commodity_name = commodity_pair[1]
            mi.commodity_price = ci.get("regularMarketPrice") or ci.get("previousClose")
            mi.commodity_52w_high = ci.get("fiftyTwoWeekHigh")
            mi.commodity_52w_low = ci.get("fiftyTwoWeekLow")
            if mi.commodity_price and mi.commodity_52w_high and mi.commodity_52w_low:
                rng = mi.commodity_52w_high - mi.commodity_52w_low
                if rng > 0:
                    mi.commodity_52w_position = (mi.commodity_price - mi.commodity_52w_low) / rng
    except Exception:
        pass

    # Fetch sector ETF performance
    try:
        etf_list = _SECTOR_ETFS.get(company_commodity, _SECTOR_ETFS[Commodity.OTHER])
        if len(etf_list) >= 1:
            etf_ticker, etf_name = etf_list[0]
            et = yf.Ticker(etf_ticker)
            ei = et.info or {}
            mi.sector_etf_name = etf_name
            mi.sector_etf_ticker = etf_ticker
            mi.sector_etf_price = ei.get("regularMarketPrice") or ei.get("previousClose")
            try:
                hist = et.history(period="3mo")
                if hist is not None and len(hist) > 1:
                    mi.sector_etf_3m_perf = (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1)
            except Exception:
                pass
        if len(etf_list) >= 2:
            etf_ticker2, etf_name2 = etf_list[1]
            et2 = yf.Ticker(etf_ticker2)
            ei2 = et2.info or {}
            mi.peer_etf_name = etf_name2
            mi.peer_etf_ticker = etf_ticker2
            mi.peer_etf_price = ei2.get("regularMarketPrice") or ei2.get("previousClose")
            try:
                hist2 = et2.history(period="3mo")
                if hist2 is not None and len(hist2) > 1:
                    mi.peer_etf_3m_perf = (hist2["Close"].iloc[-1] / hist2["Close"].iloc[0] - 1)
            except Exception:
                pass
    except Exception:
        pass

    # ── 6. Projected dilution (pre-operational utility developers) ────
    pre_revenue_stages = (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER, CompanyStage.DEVELOPER)
    if stage in pre_revenue_stages:
        runway = solvency.cash_runway_years if solvency else None
        burn = solvency.cash_burn_rate if solvency else None
        if runway is not None and runway < 3 and burn is not None and burn < 0:
            if price and price > 0 and shares_outstanding and shares_outstanding > 0:
                new_shares = abs(burn) * 2 / price
                mi.projected_dilution_annual_pct = (new_shares / 2) / shares_outstanding
                mi.projected_shares_in_2y = shares_outstanding + new_shares

        if runway is not None:
            if runway < 1:
                mi.financing_warning = (
                    "Critical: cash runway under 1 year. "
                    "Imminent dilutive financing expected."
                )
            elif runway < 1.5:
                mi.financing_warning = (
                    "Warning: cash runway under 18 months. "
                    "Dilutive financing likely within next year."
                )
            elif runway < 3:
                mi.financing_warning = (
                    "Note: cash runway under 3 years. "
                    "Future financing probable; monitor cash position."
                )

    # ── 7. Risk warnings ────────────────────────────────────────────
    warnings: list[str] = []

    if mi.beta and mi.beta > 2.0:
        warnings.append(
            f"High volatility (beta {mi.beta:.1f}) "
            "— price swings of 2-3x market moves"
        )

    if short_pct > 10:
        warnings.append(
            f"Elevated short interest ({short_pct:.1f}%) "
            "— negative sentiment or squeeze setup"
        )

    if not mi.analyst_count or mi.analyst_count == 0:
        warnings.append("No analyst coverage — higher information asymmetry")

    if mi.pct_from_52w_low is not None and mi.pct_from_52w_low < 0.20:
        warnings.append(
            "Trading near 52-week low — potential capitulation or value"
        )

    if mi.insider_buy_signal == "Insider selling":
        warnings.append("Recent insider selling detected")

    if solvency and solvency.cash_runway_years is not None and solvency.cash_runway_years < 1.5:
        warnings.append("Cash runway under 18 months — dilutive financing likely")

    if share_structure and share_structure.fully_diluted_shares:
        if share_structure.fully_diluted_shares > 500_000_000:
            warnings.append("Bloated share structure limits per-share upside")

    if stage in pre_revenue_stages and solvency and solvency.total_debt and solvency.total_debt > 0:
        warnings.append("Debt in pre-revenue company — unusual and risky")

    mi.risk_warnings = warnings

    # ── 8. Utilities disclaimers ─────────────────────────────────────
    disclaimers: list[str] = [
        "Utilities are interest-rate-sensitive. Rising long rates compress sector multiples and raise the cost of incremental capital.",
        "Regulated returns depend on the constructiveness of the regulator and the outcome of pending rate cases.",
        "Fuel-cost and purchased-power recovery can lag during volatile commodity periods, temporarily pressuring earnings.",
    ]
    if stage in (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER):
        disclaimers.append(
            "This company is pre-operational. Valuation is speculative and based "
            "on the development pipeline and PPA coverage, not cash flows from operations."
        )
    if stage == CompanyStage.DEVELOPER:
        disclaimers.append(
            "Construction cost overruns of 10-25% above initial estimates are common in utility-scale "
            "projects; regulator disallowance of imprudent costs can further compress returns."
        )
    disclaimers.extend([
        "Past performance and insider activity do not guarantee future results.",
        "This analysis is for informational purposes only and does not constitute investment advice.",
    ])
    mi.disclaimers = disclaimers

    return mi


def _calc_roic_history(statements: list[FinancialStatement]) -> list[Optional[float]]:
    vals = []
    for s in statements:
        if s.operating_income is not None and s.total_assets and s.total_cash is not None:
            nopat = s.operating_income * 0.75
            ic = s.total_assets - (s.total_cash or 0)
            if ic > 0:
                vals.append(nopat / ic)
    return vals


def _calc_margin_history(statements: list[FinancialStatement]) -> list[Optional[float]]:
    margins = []
    for s in statements:
        if s.gross_profit and s.revenue and s.revenue > 0:
            margins.append(s.gross_profit / s.revenue)
    return margins


def _cagr(start: Optional[float], end: Optional[float], years: int) -> Optional[float]:
    if not start or not end or start <= 0 or end <= 0 or years <= 0:
        return None
    try:
        result = (end / start) ** (1 / years) - 1
        if math.isnan(result) or math.isinf(result):
            return None
        return result
    except (ValueError, OverflowError, ZeroDivisionError):
        return None
