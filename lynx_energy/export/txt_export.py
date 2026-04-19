"""Plain text export — full analysis report with all sections."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Optional

from lynx_energy.models import AnalysisReport, CompanyStage


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

W = 70  # report width


def _safe(val, default=None):
    """Return val as float if valid, else default."""
    if val is None or isinstance(val, bool):
        return default
    try:
        f = float(val)
        return default if (math.isnan(f) or math.isinf(f)) else f
    except (TypeError, ValueError):
        return default


def _fmt_num(val, decimals: int = 1, suffix: str = "") -> str:
    """Format a number with magnitude suffix (K/M/B)."""
    v = _safe(val)
    if v is None:
        return "N/A"
    abs_v = abs(v)
    if abs_v >= 1e9:
        return f"{v / 1e9:,.{decimals}f}B{suffix}"
    if abs_v >= 1e6:
        return f"{v / 1e6:,.{decimals}f}M{suffix}"
    if abs_v >= 1e3:
        return f"{v / 1e3:,.{decimals}f}K{suffix}"
    return f"{v:,.{decimals}f}{suffix}"


def _fmt_pct(val, decimals: int = 1) -> str:
    """Format a decimal ratio as percentage string."""
    v = _safe(val)
    if v is None:
        return "N/A"
    return f"{v * 100:,.{decimals}f}%"


def _fmt_money(val, decimals: int = 2, currency: str = "$") -> str:
    """Format a dollar amount with magnitude suffix."""
    v = _safe(val)
    if v is None:
        return "N/A"
    abs_v = abs(v)
    sign = "-" if v < 0 else ""
    if abs_v >= 1e9:
        return f"{sign}{currency}{abs_v / 1e9:,.{decimals}f}B"
    if abs_v >= 1e6:
        return f"{sign}{currency}{abs_v / 1e6:,.{decimals}f}M"
    if abs_v >= 1e3:
        return f"{sign}{currency}{abs_v / 1e3:,.{decimals}f}K"
    return f"{sign}{currency}{abs_v:,.{decimals}f}"


def _fmt_ratio(val, decimals: int = 2) -> str:
    v = _safe(val)
    if v is None:
        return "N/A"
    return f"{v:,.{decimals}f}"


def _fmt_bool(val) -> str:
    if val is None:
        return "N/A"
    return "Yes" if val else "No"


def _row(label: str, value: str, width: int = W) -> str:
    """Format a label-value row with right-aligned value."""
    gap = width - len(label) - len(value)
    if gap < 2:
        gap = 2
    return f"  {label}{'.' * gap}{value}"


def _section(title: str) -> list[str]:
    return ["", title, "-" * W]


def _header(title: str) -> list[str]:
    return ["=" * W, title, "=" * W]


# ---------------------------------------------------------------------------
# Main export
# ---------------------------------------------------------------------------

def export_txt(report: AnalysisReport, output_path: Path) -> Path:
    from lynx_energy.core.conclusion import generate_conclusion

    p = report.profile
    c = generate_conclusion(report)
    lines: list[str] = []

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    def _ev(val):
        return val.value if hasattr(val, "value") else str(val) if val else "N/A"

    lines += _header(f"LYNX Energy  --  {p.name} ({p.ticker})")
    lines.append(f"  Tier: {_ev(p.tier)}  |  Stage: {_ev(p.stage)}")
    lines.append(f"  Commodity: {_ev(p.primary_commodity)}  |  Jurisdiction: {_ev(p.jurisdiction_tier)}")
    if p.jurisdiction_country:
        lines.append(f"  Jurisdiction country: {p.jurisdiction_country}")

    # ------------------------------------------------------------------
    # Company Profile
    # ------------------------------------------------------------------
    lines += _section("COMPANY PROFILE")
    lines.append(_row("Sector", p.sector or "N/A"))
    lines.append(_row("Industry", p.industry or "N/A"))
    lines.append(_row("Country", p.country or "N/A"))
    lines.append(_row("Exchange", p.exchange or "N/A"))
    lines.append(_row("Currency", p.currency or "N/A"))
    lines.append(_row("Market Cap", _fmt_money(p.market_cap)))
    if p.employees:
        lines.append(_row("Employees", f"{p.employees:,}"))
    if p.website:
        lines.append(_row("Website", p.website))
    if p.isin:
        lines.append(_row("ISIN", p.isin))

    # ------------------------------------------------------------------
    # Valuation Metrics
    # ------------------------------------------------------------------
    if report.valuation:
        v = report.valuation
        lines += _section("VALUATION METRICS")
        _fields = [
            ("P/E (Trailing)", _fmt_ratio(v.pe_trailing)),
            ("P/E (Forward)", _fmt_ratio(v.pe_forward)),
            ("P/B Ratio", _fmt_ratio(v.pb_ratio)),
            ("P/S Ratio", _fmt_ratio(v.ps_ratio)),
            ("P/FCF", _fmt_ratio(v.p_fcf)),
            ("EV/EBITDA", _fmt_ratio(v.ev_ebitda)),
            ("EV/Revenue", _fmt_ratio(v.ev_revenue)),
            ("PEG Ratio", _fmt_ratio(v.peg_ratio)),
            ("Dividend Yield", _fmt_pct(v.dividend_yield)),
            ("Earnings Yield", _fmt_pct(v.earnings_yield)),
            ("Enterprise Value", _fmt_money(v.enterprise_value)),
            ("Market Cap", _fmt_money(v.market_cap)),
            ("P/Tangible Book", _fmt_ratio(v.price_to_tangible_book)),
            ("P/NCAV", _fmt_ratio(v.price_to_ncav)),
            ("EV/BOE Reserves", _fmt_money(v.ev_per_boe)),
            ("EV/MCFE Reserves", _fmt_money(v.ev_per_mcfe)),
            ("P/NAV", _fmt_ratio(v.p_nav)),
            ("Cash/Market Cap", _fmt_pct(v.cash_to_market_cap)),
            ("NAV/Share", _fmt_money(v.nav_per_share)),
        ]
        for label, val in _fields:
            if val != "N/A":
                lines.append(_row(label, val))

    # ------------------------------------------------------------------
    # Profitability Metrics
    # ------------------------------------------------------------------
    lines += _section("PROFITABILITY METRICS")
    _pre_revenue = _ev(p.stage) in ("Grassroots Explorer", "Advanced Explorer")
    if _pre_revenue:
        lines.append("  N/A for pre-revenue company at this stage.")
        if report.profitability and report.profitability.netback_per_boe is not None:
            lines.append(_row("Netback/" + report.profitability.netback_unit, _fmt_money(report.profitability.netback_per_boe)))
    elif report.profitability:
        pr = report.profitability
        _fields = [
            ("ROE", _fmt_pct(pr.roe)),
            ("ROA", _fmt_pct(pr.roa)),
            ("ROIC", _fmt_pct(pr.roic)),
            ("Gross Margin", _fmt_pct(pr.gross_margin)),
            ("Operating Margin", _fmt_pct(pr.operating_margin)),
            ("Net Margin", _fmt_pct(pr.net_margin)),
            ("FCF Margin", _fmt_pct(pr.fcf_margin)),
            ("EBITDA Margin", _fmt_pct(pr.ebitda_margin)),
            ("Netback/" + pr.netback_unit, _fmt_money(pr.netback_per_boe)),
            ("Op. Cost/" + pr.netback_unit, _fmt_money(pr.operating_cost_per_boe)),
            ("Netback Margin", _fmt_pct(pr.netback_margin)),
        ]
        for label, val in _fields:
            if val != "N/A":
                lines.append(_row(label, val))
    else:
        lines.append("  No profitability data available.")

    # ------------------------------------------------------------------
    # Solvency & Survival
    # ------------------------------------------------------------------
    if report.solvency:
        s = report.solvency
        lines += _section("SOLVENCY & SURVIVAL")
        _fields = [
            ("Total Cash", _fmt_money(s.total_cash)),
            ("Total Debt", _fmt_money(s.total_debt)),
            ("Net Debt", _fmt_money(s.net_debt)),
            ("Cash/Share", _fmt_money(s.cash_per_share)),
            ("Cash Burn Rate (annual)", _fmt_money(s.cash_burn_rate)),
            ("Quarterly Burn Rate", _fmt_money(s.quarterly_burn_rate)),
            ("Cash Runway", f"{s.cash_runway_years:.1f} years" if _safe(s.cash_runway_years) is not None else "N/A"),
            ("Burn % of Mkt Cap", _fmt_pct(s.burn_as_pct_of_market_cap)),
            ("Debt/Equity", _fmt_ratio(s.debt_to_equity)),
            ("Debt/EBITDA", _fmt_ratio(s.debt_to_ebitda)),
            ("Current Ratio", _fmt_ratio(s.current_ratio)),
            ("Quick Ratio", _fmt_ratio(s.quick_ratio)),
            ("Interest Coverage", _fmt_ratio(s.interest_coverage)),
            ("Working Capital", _fmt_money(s.working_capital)),
            ("Altman Z-Score", _fmt_ratio(s.altman_z_score)),
            ("Tangible Book Value", _fmt_money(s.tangible_book_value)),
            ("NCAV", _fmt_money(s.ncav)),
            ("NCAV/Share", _fmt_money(s.ncav_per_share)),
        ]
        for label, val in _fields:
            if val != "N/A":
                lines.append(_row(label, val))

    # ------------------------------------------------------------------
    # Growth & Dilution
    # ------------------------------------------------------------------
    if report.growth:
        g = report.growth
        lines += _section("GROWTH & DILUTION")
        _fields = [
            ("Revenue Growth (YoY)", _fmt_pct(g.revenue_growth_yoy)),
            ("Revenue CAGR 3Y", _fmt_pct(g.revenue_cagr_3y)),
            ("Revenue CAGR 5Y", _fmt_pct(g.revenue_cagr_5y)),
            ("Earnings Growth (YoY)", _fmt_pct(g.earnings_growth_yoy)),
            ("Earnings CAGR 3Y", _fmt_pct(g.earnings_cagr_3y)),
            ("Earnings CAGR 5Y", _fmt_pct(g.earnings_cagr_5y)),
            ("FCF Growth (YoY)", _fmt_pct(g.fcf_growth_yoy)),
            ("Book Value Growth (YoY)", _fmt_pct(g.book_value_growth_yoy)),
            ("Dividend Growth 5Y", _fmt_pct(g.dividend_growth_5y)),
            ("Share Dilution (YoY)", _fmt_pct(g.shares_growth_yoy)),
            ("Share Dilution CAGR 3Y", _fmt_pct(g.shares_growth_3y_cagr)),
            ("Fully Diluted Shares", _fmt_num(g.fully_diluted_shares, 0)),
            ("Dilution Ratio", _fmt_ratio(g.dilution_ratio)),
            ("Production Growth (YoY)", _fmt_pct(g.production_growth_yoy)),
        ]
        for label, val in _fields:
            if val != "N/A":
                lines.append(_row(label, val))

    # ------------------------------------------------------------------
    # Share Structure
    # ------------------------------------------------------------------
    if report.share_structure:
        ss = report.share_structure
        lines += _section("SHARE STRUCTURE")
        _fields = [
            ("Shares Outstanding", _fmt_num(ss.shares_outstanding, 0)),
            ("Fully Diluted Shares", _fmt_num(ss.fully_diluted_shares, 0)),
            ("Warrants Outstanding", _fmt_num(ss.warrants_outstanding, 0)),
            ("Options Outstanding", _fmt_num(ss.options_outstanding, 0)),
            ("Float Shares", _fmt_num(ss.float_shares, 0)),
            ("Insider Ownership", _fmt_pct(ss.insider_ownership_pct)),
            ("Institutional Ownership", _fmt_pct(ss.institutional_ownership_pct)),
            ("Assessment", ss.share_structure_assessment or "N/A"),
            ("Warrant Overhang Risk", ss.warrant_overhang_risk or "N/A"),
        ]
        for label, val in _fields:
            if val != "N/A":
                lines.append(_row(label, val))

    # ------------------------------------------------------------------
    # Energy Quality Indicators
    # ------------------------------------------------------------------
    if report.energy_quality:
        mq = report.energy_quality
        lines += _section("ENERGY QUALITY INDICATORS")
        _fields = [
            ("Quality Score", f"{mq.quality_score:.0f}/100" if _safe(mq.quality_score) is not None else "N/A"),
            ("Competitive Position", mq.competitive_position or "N/A"),
            ("Management Quality", mq.management_quality or "N/A"),
            ("Management Track Record", mq.management_track_record or "N/A"),
            ("Insider Ownership", _fmt_pct(mq.insider_ownership_pct)),
            ("Insider Alignment", mq.insider_alignment or "N/A"),
            ("Jurisdiction Assessment", mq.jurisdiction_assessment or "N/A"),
            ("Jurisdiction Score", f"{mq.jurisdiction_score:.0f}" if _safe(mq.jurisdiction_score) is not None else "N/A"),
            ("Reserve Quality", mq.reserve_quality or "N/A"),
            ("Reserve Life", mq.reserve_life_assessment or "N/A"),
            ("Production Scale", mq.production_scale_assessment or "N/A"),
            ("Financial Position", mq.financial_position or "N/A"),
            ("Dilution Risk", mq.dilution_risk or "N/A"),
            ("Share Structure", mq.share_structure_assessment or "N/A"),
            ("Catalyst Density", mq.catalyst_density or "N/A"),
            ("Strategic Backing", mq.strategic_backing or "N/A"),
            ("Asset Backing", mq.asset_backing or "N/A"),
            ("Niche Position", mq.niche_position or "N/A"),
            ("Revenue Predictability", mq.revenue_predictability or "N/A"),
        ]
        for label, val in _fields:
            if val != "N/A":
                lines.append(_row(label, val))
        if mq.near_term_catalysts:
            lines.append("")
            lines.append("  Near-term Catalysts:")
            for cat in mq.near_term_catalysts:
                lines.append(f"    * {cat}")

    # ------------------------------------------------------------------
    # Intrinsic Value
    # ------------------------------------------------------------------
    if report.intrinsic_value:
        iv = report.intrinsic_value
        lines += _section("INTRINSIC VALUE ESTIMATES")
        lines.append(_row("Current Price", _fmt_money(iv.current_price)))
        lines.append(_row("Primary Method", iv.primary_method or "N/A"))
        lines.append(_row("Secondary Method", iv.secondary_method or "N/A"))
        lines.append("")

        def _iv_row(name: str, val_field, mos_field) -> Optional[str]:
            v = _safe(val_field)
            if v is None:
                return None
            mos = _safe(mos_field)
            mos_str = f"  (MoS: {mos * 100:+.0f}%)" if mos is not None else ""
            return _row(name, f"{_fmt_money(val_field)}{mos_str}")

        rows = [
            _iv_row("DCF Value", iv.dcf_value, iv.margin_of_safety_dcf),
            _iv_row("Graham Number", iv.graham_number, iv.margin_of_safety_graham),
            _iv_row("Lynch Fair Value", iv.lynch_fair_value, None),
            _iv_row("NCAV Value", iv.ncav_value, iv.margin_of_safety_ncav),
            _iv_row("Asset-Based Value", iv.asset_based_value, iv.margin_of_safety_asset),
            _iv_row("NAV/Share", iv.nav_per_share, iv.margin_of_safety_nav),
            _iv_row("EV/Reserve Implied", iv.ev_reserve_implied_price, None),
        ]
        for r in rows:
            if r is not None:
                lines.append(r)

    # ------------------------------------------------------------------
    # Market Intelligence
    # ------------------------------------------------------------------
    if report.market_intelligence:
        mi = report.market_intelligence
        lines += _section("MARKET INTELLIGENCE")

        # Commodity & Sector Context
        if mi.commodity_name or mi.sector_etf_name:
            lines.append("")
            lines.append("  Commodity & Sector Context:")
            if mi.commodity_name and mi.commodity_price:
                lines.append(_row("Commodity", f"{mi.commodity_name} -- ${mi.commodity_price:,.2f}"))
                if mi.commodity_52w_high and mi.commodity_52w_low:
                    lines.append(_row("52W Range", f"${mi.commodity_52w_low:,.2f} - ${mi.commodity_52w_high:,.2f}"))
            if mi.sector_etf_name:
                perf = f" ({mi.sector_etf_3m_perf*100:+.1f}% 3m)" if mi.sector_etf_3m_perf is not None else ""
                lines.append(_row("Sector ETF", f"{mi.sector_etf_name}{perf}"))
            if mi.peer_etf_name:
                perf = f" ({mi.peer_etf_3m_perf*100:+.1f}% 3m)" if mi.peer_etf_3m_perf is not None else ""
                lines.append(_row("Peer ETF", f"{mi.peer_etf_name}{perf}"))

        # Analyst Consensus
        lines.append("")
        lines.append("  Analyst Consensus:")
        _fields = [
            ("Recommendation", mi.recommendation or "N/A"),
            ("Analyst Count", str(mi.analyst_count) if mi.analyst_count is not None else "N/A"),
            ("Target High", _fmt_money(mi.target_high)),
            ("Target Low", _fmt_money(mi.target_low)),
            ("Target Mean", _fmt_money(mi.target_mean)),
            ("Target Upside", _fmt_pct(mi.target_upside_pct)),
        ]
        for label, val in _fields:
            if val != "N/A":
                lines.append(_row(label, val))

        # Short Interest
        lines.append("")
        lines.append("  Short Interest:")
        _fields = [
            ("Shares Short", _fmt_num(mi.shares_short, 0)),
            ("Short % of Float", _fmt_pct(mi.short_pct_of_float)),
            ("Days to Cover", _fmt_ratio(mi.short_ratio_days)),
            ("Short Squeeze Risk", mi.short_squeeze_risk or "N/A"),
        ]
        for label, val in _fields:
            if val != "N/A":
                lines.append(_row(label, val))

        # Price Technicals
        lines.append("")
        lines.append("  Price & Technicals:")
        _fields = [
            ("Current Price", _fmt_money(mi.price_current)),
            ("52W High", _fmt_money(mi.price_52w_high)),
            ("52W Low", _fmt_money(mi.price_52w_low)),
            ("% from 52W High", _fmt_pct(mi.pct_from_52w_high)),
            ("% from 52W Low", _fmt_pct(mi.pct_from_52w_low)),
            ("52W Range Position", _fmt_pct(mi.price_52w_range_position)),
            ("SMA 50", _fmt_money(mi.sma_50)),
            ("SMA 200", _fmt_money(mi.sma_200)),
            ("Above SMA 50", _fmt_bool(mi.above_sma_50)),
            ("Above SMA 200", _fmt_bool(mi.above_sma_200)),
            ("Golden Cross", _fmt_bool(mi.golden_cross)),
            ("Beta", _fmt_ratio(mi.beta)),
            ("Avg Volume", _fmt_num(mi.avg_volume, 0)),
            ("10D Avg Volume", _fmt_num(mi.volume_10d_avg, 0)),
            ("Volume Trend", mi.volume_trend or "N/A"),
        ]
        for label, val in _fields:
            if val != "N/A":
                lines.append(_row(label, val))

        # Insider Signal
        lines.append("")
        lines.append("  Insider Activity:")
        _fields = [
            ("Insider Buy Signal", mi.insider_buy_signal or "N/A"),
            ("Net Insider Shares (3M)", _fmt_num(mi.net_insider_shares_3m, 0)),
        ]
        for label, val in _fields:
            if val != "N/A":
                lines.append(_row(label, val))
        if mi.insider_transactions:
            lines.append("")
            lines.append("  Recent Insider Transactions:")
            for t in mi.insider_transactions[:5]:
                # Handle both InsiderTransaction dataclass and plain dict (from cache)
                _g = lambda k, d="": t.get(k, d) if isinstance(t, dict) else getattr(t, k, d)
                val_str = f" ({_fmt_money(_g('value'))})" if _g('value') else ""
                insider = str(_g('insider', ''))[:25]
                lines.append(f"    {_g('date')}  {insider:<25s}  {_g('transaction_type')}  {_fmt_num(_g('shares'), 0)} shs{val_str}")

        # Institutional
        if mi.institutions_count or mi.institutions_pct or mi.top_holders:
            lines.append("")
            lines.append("  Institutional Holdings:")
            if mi.institutions_count is not None:
                lines.append(_row("Institutions Count", str(mi.institutions_count)))
            if mi.institutions_pct is not None:
                lines.append(_row("Institutional %", _fmt_pct(mi.institutions_pct)))
            if mi.top_holders:
                lines.append("  Top Holders:")
                for h in mi.top_holders[:5]:
                    lines.append(f"    * {h}")

        # Projected Dilution
        if mi.projected_dilution_annual_pct or mi.financing_warning:
            lines.append("")
            lines.append("  Projected Dilution:")
            if mi.projected_dilution_annual_pct is not None:
                lines.append(_row("Annual Dilution Rate", _fmt_pct(mi.projected_dilution_annual_pct)))
            if mi.projected_shares_in_2y is not None:
                lines.append(_row("Projected Shares (2Y)", _fmt_num(mi.projected_shares_in_2y, 0)))
            if mi.financing_warning:
                lines.append(f"  WARNING: {mi.financing_warning}")

        # Risk Warnings
        if mi.risk_warnings:
            lines.append("")
            lines.append("  Risk Warnings:")
            for w_msg in mi.risk_warnings:
                lines.append(f"    !! {w_msg}")

        # Disclaimers
        if mi.disclaimers:
            lines.append("")
            lines.append("  Disclaimers:")
            for d in mi.disclaimers:
                lines.append(f"    * {d}")

    # ------------------------------------------------------------------
    # Conclusion
    # ------------------------------------------------------------------
    lines += [""]
    lines += _header("CONCLUSION")
    lines.append(f"  Verdict: {c.verdict}  --  Overall Score: {c.overall_score:.0f}/100")
    lines.append("")
    lines.append(f"  {c.summary}")

    # Category Scores
    if c.category_scores:
        lines.append("")
        lines.append("  Category Scores:")
        lines.append("  " + "-" * 40)
        for cat, score in c.category_scores.items():
            bar_len = int(score / 100 * 20)
            bar = "#" * bar_len + "." * (20 - bar_len)
            label = cat.replace("_", " ").title()
            lines.append(f"    {label:<20s} [{bar}] {score:5.1f}")

    # Strengths & Risks
    if c.strengths:
        lines.append("")
        lines.append("  Strengths:")
        for s_item in c.strengths:
            lines.append(f"    + {s_item}")
    if c.risks:
        lines.append("")
        lines.append("  Risks:")
        for r_item in c.risks:
            lines.append(f"    - {r_item}")

    # Screening Checklist
    if c.screening_checklist:
        lines.append("")
        lines.append("  Energy Screening Checklist:")
        lines.append("  " + "-" * 40)
        for check, result in c.screening_checklist.items():
            label = check.replace("_", " ").title()
            if result is True:
                status = "PASS"
            elif result is False:
                status = "FAIL"
            else:
                status = "N/A"
            lines.append(f"    {label:<30s} [{status:>4s}]")

    # Stage & Tier Notes
    if c.tier_note:
        lines.append("")
        lines.append(f"  Tier note: {c.tier_note}")
    if c.stage_note:
        lines.append(f"  Stage note: {c.stage_note}")

    # ------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------
    lines.append("")
    lines += _header("END OF REPORT")
    lines.append(f"  Generated: {report.fetched_at}")
    lines.append(f"  Lynx Energy Analysis (Lince Investor Suite)")
    lines.append("=" * W)

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
