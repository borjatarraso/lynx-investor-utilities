"""Rich console display for energy analysis reports — stage and tier aware.

All metric sections use the 4-level relevance system driven by get_relevance()
with BOTH tier AND stage parameters:

  CRITICAL    — bold cyan star prefix, always shown first
  RELEVANT    — normal display with indent
  CONTEXTUAL  — dimmed display with indent
  IRRELEVANT  — completely hidden (not rendered)
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from lynx_energy.metrics.relevance import get_relevance
from lynx_energy.models import AnalysisReport, CompanyStage, CompanyTier, Relevance

console = Console()

WARN = "\u26a0"

_STYLE = {
    Relevance.CRITICAL: ("bold", "[bold cyan]*[/] "),
    Relevance.RELEVANT: ("", "  "),
    Relevance.CONTEXTUAL: ("dim", "  "),
    Relevance.IRRELEVANT: ("dim strike", "  "),
}


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _tier_color(tier):
    return {
        CompanyTier.MEGA: "bold green", CompanyTier.LARGE: "green",
        CompanyTier.MID: "cyan", CompanyTier.SMALL: "yellow",
        CompanyTier.MICRO: "#ff8800", CompanyTier.NANO: "bold red",
    }.get(tier, "white")


def _stage_color(stage):
    return {
        CompanyStage.PRODUCER: "bold green", CompanyStage.ROYALTY: "bold green",
        CompanyStage.DEVELOPER: "cyan", CompanyStage.EXPLORER: "yellow",
        CompanyStage.GRASSROOTS: "#ff8800",
    }.get(stage, "white")


def _isna(val):
    if val is None:
        return True
    try:
        import math
        return math.isnan(val)
    except (TypeError, ValueError):
        return False


def fmt_pct(val, digits=2):
    return "[dim]N/A[/]" if _isna(val) else f"{val * 100:.{digits}f}%"


def fmt_num(val, digits=2):
    return "[dim]N/A[/]" if _isna(val) else f"{val:,.{digits}f}"


def fmt_money(val):
    if _isna(val):
        return "[dim]N/A[/]"
    if abs(val) >= 1e12:
        return f"${val / 1e12:,.2f}T"
    if abs(val) >= 1e9:
        return f"${val / 1e9:,.2f}B"
    if abs(val) >= 1e6:
        return f"${val / 1e6:,.2f}M"
    return f"${val:,.0f}"


def fmt_shares(val):
    if _isna(val):
        return "[dim]N/A[/]"
    if val >= 1e9:
        return f"{val / 1e9:,.1f}B"
    if val >= 1e6:
        return f"{val / 1e6:,.1f}M"
    return f"{val:,.0f}"


def fmt_score(val):
    if val is None:
        return "[dim]N/A[/]"
    if val >= 70:
        return f"[bold green]{val:.1f}/100[/]"
    if val >= 45:
        return f"[bold yellow]{val:.1f}/100[/]"
    if val >= 20:
        return f"[bold #ff8800]{val:.1f}/100[/]"
    return f"[bold red]{val:.1f}/100[/]"


def _mos_color(val):
    if val is None:
        return "[dim]N/A[/]"
    pct = val * 100
    if pct > 25:
        return f"[bold green]{pct:.1f}% (Undervalued)[/]"
    if pct > 0:
        return f"[yellow]{pct:.1f}% (Slight Undervalue)[/]"
    return f"[bold red]{pct:.1f}% (Overvalued)[/]"


# ---------------------------------------------------------------------------
# Row helper — handles relevance-based styling + IRRELEVANT hiding
# ---------------------------------------------------------------------------

def _add_metric_row(table, label, value, assessment, relevance, *, has_assessment_col=True):
    """Add a styled row to a table, hiding IRRELEVANT metrics entirely."""
    if relevance == Relevance.IRRELEVANT:
        return
    style, prefix = _STYLE[relevance]
    sl = f"{prefix}[{style}]{label}[/]" if style else f"{prefix}{label}"
    sv = f"[{style}]{value}[/]" if style else value
    if has_assessment_col:
        sa = f"[{style}]{assessment}[/]" if style else assessment
        table.add_row(sl, sv, sa)
    else:
        table.add_row(sl, sv)


# ---------------------------------------------------------------------------
# Assessment functions — all return meaningful text for energy context
# Severity markers: *CRITICAL*, *WARNING*, *WATCH*, *OK*, *STRONG*
# ---------------------------------------------------------------------------

def _a_pe(val):
    if _isna(val):
        return "[dim]No earnings data[/]"
    if val < 0:
        return "[red]*WARNING* Negative earnings — common in pre-production energy companies[/]"
    if val < 8:
        return "[bold green]*STRONG* Deep value — verify earnings are sustainable[/]"
    if val < 12:
        return "[green]*OK* Very cheap — typical of cyclical commodity lows[/]"
    if val < 18:
        return "[green]*OK* Reasonably valued for a producing energy company[/]"
    if val < 25:
        return "[yellow]*WATCH* Fair — pricing in production growth[/]"
    if val < 40:
        return "[#ff8800]*WARNING* Expensive — needs strong production catalysts[/]"
    return "[red]*CRITICAL* Very expensive — cycle peak or speculative premium[/]"


def _a_pb(val):
    if _isna(val):
        return "[dim]No book value data[/]"
    if val < 0.5:
        return "[bold green]*STRONG* Deep discount to assets — check for impairments[/]"
    if val < 1.0:
        return "[green]*OK* Below book — potential asset value play[/]"
    if val < 1.5:
        return "[green]*OK* Near book value — reasonable for energy companies[/]"
    if val < 2.5:
        return "[yellow]*WATCH* Above book — market pricing in resource upside[/]"
    if val < 4.0:
        return "[#ff8800]*WARNING* Premium to assets — needs exceptional resources[/]"
    return "[red]*CRITICAL* High premium — speculative or trophy asset pricing[/]"


def _a_ps(val):
    if _isna(val):
        return "[dim]No revenue — pre-production stage[/]"
    if val < 1.0:
        return "[bold green]*STRONG* Very cheap on revenue basis[/]"
    if val < 2.0:
        return "[green]*OK* Cheap — typical of mature commodity producers[/]"
    if val < 4.0:
        return "[yellow]*WATCH* Fair for a growing producer[/]"
    if val < 8.0:
        return "[#ff8800]*WARNING* Rich — needs margin expansion to justify[/]"
    return "[red]*CRITICAL* Very expensive on revenue basis[/]"


def _a_pfcf(val):
    if _isna(val):
        return "[dim]No FCF — pre-production or capex heavy[/]"
    if val < 0:
        return "[red]*CRITICAL* Negative FCF — burning cash or heavy capex cycle[/]"
    if val < 8:
        return "[bold green]*STRONG* Strong FCF yield — cash-generative energy company[/]"
    if val < 15:
        return "[green]*OK* Good FCF generation[/]"
    if val < 25:
        return "[yellow]*WATCH* Moderate — reinvesting heavily[/]"
    return "[#ff8800]*WARNING* Low FCF yield relative to price[/]"


def _a_ev(val):
    if _isna(val):
        return "[dim]Insufficient data for EV/EBITDA[/]"
    if val < 0:
        return "[red]*CRITICAL* Negative EBITDA — operational losses[/]"
    if val < 4:
        return "[bold green]*STRONG* Very cheap — verify EBITDA sustainability[/]"
    if val < 6:
        return "[green]*OK* Cheap for a producing energy company[/]"
    if val < 9:
        return "[yellow]*WATCH* Fair — mid-cycle valuation[/]"
    if val < 14:
        return "[#ff8800]*WARNING* Rich — pricing in growth or cycle upturn[/]"
    return "[red]*CRITICAL* Very expensive — peak cycle risk[/]"


def _a_evrev(val):
    if _isna(val):
        return "[dim]No revenue for EV/Revenue[/]"
    if val < 1.5:
        return "[green]*OK* Low EV/Revenue — value territory[/]"
    if val < 3.0:
        return "[yellow]*WATCH* Fair for energy[/]"
    if val < 6.0:
        return "[#ff8800]*WARNING* Elevated — needs high margins[/]"
    return "[red]*CRITICAL* Very high — speculative premium[/]"


def _a_peg(val):
    if _isna(val):
        return "[dim]No PEG data — growth/earnings unavailable[/]"
    if val < 0:
        return "[red]*CRITICAL* Negative — declining earnings[/]"
    if val < 0.5:
        return "[bold green]*STRONG* Attractive growth-adjusted value[/]"
    if val < 1.0:
        return "[green]*OK* Fair growth-adjusted valuation[/]"
    if val < 2.0:
        return "[yellow]*WATCH* Paying up for growth[/]"
    return "[#ff8800]*WARNING* Expensive relative to growth rate[/]"


def _a_ey(val):
    if _isna(val):
        return "[dim]No earnings yield data[/]"
    if val > 0.12:
        return "[bold green]*STRONG* High yield — deep value if sustainable[/]"
    if val > 0.08:
        return "[green]*OK* Attractive earnings yield[/]"
    if val > 0.05:
        return "[yellow]*WATCH* Moderate yield[/]"
    if val > 0:
        return "[#ff8800]*WARNING* Low yield — priced for growth[/]"
    return "[red]*CRITICAL* Negative yield — no earnings[/]"


def _a_divy(val):
    if _isna(val):
        return "[dim]No dividend — typical for junior energy companies[/]"
    if val == 0:
        return "[dim]No dividend paid[/]"
    if val > 0.06:
        return "[bold green]*STRONG* High yield — verify sustainability with FCF[/]"
    if val > 0.03:
        return "[green]*OK* Solid yield for an energy company[/]"
    if val > 0.01:
        return "[yellow]*WATCH* Modest yield — signal of cash generation[/]"
    return "[dim]Token dividend[/]"


def _a_ptb(val):
    if _isna(val):
        return "[dim]No tangible book data[/]"
    if val < 0.5:
        return "[bold green]*STRONG* Deep discount to tangible assets[/]"
    if val < 1.0:
        return "[green]*OK* Below tangible book — asset-backed value[/]"
    if val < 2.0:
        return "[yellow]*WATCH* Above tangible book[/]"
    return "[#ff8800]*WARNING* High premium to tangible assets[/]"


def _a_pncav(val):
    if _isna(val):
        return "[dim]NCAV not meaningful[/]"
    if val < 0:
        return "[dim]Negative NCAV — liabilities exceed current assets[/]"
    if val < 0.67:
        return "[bold green]*STRONG* Graham net-net — trading below liquidation value[/]"
    if val < 1.0:
        return "[green]*OK* Below NCAV — potential deep value[/]"
    if val < 1.5:
        return "[yellow]*WATCH* Near NCAV[/]"
    return "[dim]Above NCAV — not a net-net[/]"


def _a_ctm(val):
    if _isna(val):
        return "[dim]No cash/market cap data[/]"
    if val > 0.60:
        return "[bold green]*STRONG* Near cash-shell — strong downside protection[/]"
    if val > 0.40:
        return "[bold green]*STRONG* High cash backing — significant floor[/]"
    if val > 0.25:
        return "[green]*OK* Good cash backing relative to market cap[/]"
    if val > 0.15:
        return "[yellow]*WATCH* Moderate cash position[/]"
    if val > 0.05:
        return "[#ff8800]*WARNING* Low cash backing — financing risk for explorers[/]"
    return "[red]*CRITICAL* Minimal cash — fundraising likely imminent[/]"


# --- Market intelligence assessments ---

def _a_recommendation(val):
    if not val: return ""
    v = val.lower()
    if "strong_buy" in v: return "[bold green]*STRONG* Strong consensus — high conviction[/]"
    if "buy" in v: return "[green]*OK* Positive consensus[/]"
    if "hold" in v: return "[yellow]*WATCH* Neutral consensus[/]"
    if "sell" in v: return "[red]*WARNING* Negative consensus[/]"
    return ""

def _a_analyst_count(val):
    if val is None: return ""
    if val >= 10: return "[green]*OK* Well covered[/]"
    if val >= 5: return "[green]*OK* Moderate coverage[/]"
    if val >= 2: return "[yellow]*WATCH* Light coverage[/]"
    return "[dim]Minimal coverage — higher information asymmetry[/]"

def _a_target_upside(val):
    if val is None: return ""
    pct = val * 100
    if pct > 50: return f"[bold green]*STRONG* Significant upside potential ({pct:.0f}%)[/]"
    if pct > 20: return f"[green]*OK* Good upside ({pct:.0f}%)[/]"
    if pct > 0: return f"[yellow]*WATCH* Modest upside ({pct:.0f}%)[/]"
    return f"[red]*WARNING* Below target ({pct:.0f}%)[/]"

def _a_short_pct(val):
    """Assess short % of float. val is a ratio (e.g. 0.05 = 5%)."""
    if val is None: return ""
    pct = val * 100
    if pct > 20: return "[bold red]*CRITICAL* Very high short interest — extreme negative sentiment or squeeze setup[/]"
    if pct > 10: return "[red]*WARNING* Elevated — significant bearish positioning[/]"
    if pct > 5: return "[yellow]*WATCH* Moderate short interest[/]"
    return "[green]*OK* Normal levels[/]"

def _a_days_to_cover(val):
    if val is None: return ""
    if val > 10: return "[bold red]*CRITICAL* Very high days to cover — potential short squeeze[/]"
    if val > 5: return "[yellow]*WATCH* Elevated — shorts may be trapped[/]"
    return "[dim]*OK* Normal[/]"

def _a_beta(val):
    if val is None: return ""
    if val > 2.5: return "[bold red]*CRITICAL* Extreme volatility — price swings 2.5x+ market moves[/]"
    if val > 2.0: return "[red]*WARNING* High volatility — expect large price swings[/]"
    if val > 1.5: return "[yellow]*WATCH* Above-average volatility[/]"
    if val > 1.0: return "[dim]Moderate — moves with market[/]"
    if val > 0.5: return "[green]*OK* Low volatility — defensive[/]"
    return "[green]*OK* Very low beta — minimal market correlation[/]"

def _range_bar(position):
    """Visual bar showing where price is in 52-week range."""
    if position is None: return ""
    filled = int(position * 20)
    empty = 20 - filled
    bar = "[red]" + "=" * filled + "[/][dim]" + "-" * empty + "[/]"
    if position < 0.2: return f"{bar} Near 52w low"
    if position > 0.8: return f"{bar} Near 52w high"
    return bar


# --- Profitability assessments ---

def _a_roe(val):
    if _isna(val):
        return "[dim]No ROE data — pre-earnings stage[/]"
    if val < -0.20:
        return "[red]*CRITICAL* Deeply negative ROE — significant losses[/]"
    if val < 0:
        return "[#ff8800]*WARNING* Negative ROE — unprofitable period[/]"
    if val < 0.05:
        return "[yellow]*WATCH* Low ROE — below cost of equity[/]"
    if val < 0.12:
        return "[green]*OK* Adequate ROE for a cyclical energy company[/]"
    if val < 0.20:
        return "[green]*OK* Strong ROE — efficient capital deployment[/]"
    return "[bold green]*STRONG* Exceptional ROE — verify sustainability[/]"


def _a_roa(val):
    if _isna(val):
        return "[dim]No ROA data[/]"
    if val < -0.10:
        return "[red]*CRITICAL* Deeply negative — asset base eroding[/]"
    if val < 0:
        return "[#ff8800]*WARNING* Negative ROA — not generating returns on assets[/]"
    if val < 0.03:
        return "[yellow]*WATCH* Low ROA — asset-heavy industry typical[/]"
    if val < 0.08:
        return "[green]*OK* Good ROA for capital-intensive energy[/]"
    return "[bold green]*STRONG* Excellent asset efficiency[/]"


def _a_roic(val):
    if _isna(val):
        return "[dim]No ROIC data — pre-production or insufficient data[/]"
    if val < -0.10:
        return "[red]*CRITICAL* Deeply negative — destroying capital[/]"
    if val < 0:
        return "[#ff8800]*WARNING* Negative ROIC — below cost of capital[/]"
    if val < 0.06:
        return "[yellow]*WATCH* Below WACC — marginal capital allocation[/]"
    if val < 0.12:
        return "[green]*OK* ROIC above typical WACC — value creation[/]"
    if val < 0.20:
        return "[green]*OK* Strong ROIC — high-quality operations[/]"
    return "[bold green]*STRONG* Exceptional ROIC — world-class asset[/]"


def _a_gm(val):
    if _isna(val):
        return "[dim]No gross margin — pre-revenue stage[/]"
    if val < 0:
        return "[bold red]*CRITICAL* Negative gross margin — selling below cost[/]"
    if val < 0.15:
        return "[red]*WARNING* Very thin — vulnerable to commodity price swings[/]"
    if val < 0.25:
        return "[#ff8800]*WARNING* Below average — high-cost producer[/]"
    if val < 0.40:
        return "[yellow]*WATCH* Adequate gross margin for energy[/]"
    if val < 0.55:
        return "[green]*OK* Strong margins — low-cost producer[/]"
    return "[bold green]*STRONG* Exceptional — best-in-class cost structure[/]"


def _a_om(val):
    if _isna(val):
        return "[dim]No operating margin data[/]"
    if val < -0.50:
        return "[red]*CRITICAL* Heavy operating losses — explorer burn rate[/]"
    if val < 0:
        return "[#ff8800]*WARNING* Negative — G&A exceeds gross profit[/]"
    if val < 0.10:
        return "[yellow]*WATCH* Thin operating margin[/]"
    if val < 0.25:
        return "[green]*OK* Solid operating margin[/]"
    return "[bold green]*STRONG* High operating leverage — efficient operations[/]"


def _a_nm(val):
    if _isna(val):
        return "[dim]No net margin data[/]"
    if val < -0.50:
        return "[red]*CRITICAL* Deep losses — verify cash runway[/]"
    if val < 0:
        return "[#ff8800]*WARNING* Net loss — common for development-stage energy companies[/]"
    if val < 0.05:
        return "[yellow]*WATCH* Thin net margin — leverage and tax impact[/]"
    if val < 0.15:
        return "[green]*OK* Healthy net margin for an energy company[/]"
    return "[bold green]*STRONG* Strong profitability — low-cost advantage[/]"


def _a_fcfm(val):
    if _isna(val):
        return "[dim]No FCF margin — pre-production or capex heavy[/]"
    if val < -0.50:
        return "[red]*CRITICAL* Heavy cash outflows — verify funding sources[/]"
    if val < 0:
        return "[#ff8800]*WARNING* Negative FCF margin — capex cycle or exploration[/]"
    if val < 0.05:
        return "[yellow]*WATCH* Minimal FCF generation[/]"
    if val < 0.15:
        return "[green]*OK* Solid FCF conversion[/]"
    return "[bold green]*STRONG* Strong free cash flow margin[/]"


def _a_ebitdam(val):
    if _isna(val):
        return "[dim]No EBITDA margin data[/]"
    if val < 0:
        return "[red]*CRITICAL* Negative EBITDA — operational losses[/]"
    if val < 0.15:
        return "[#ff8800]*WARNING* Low EBITDA margin — high-cost structure[/]"
    if val < 0.30:
        return "[yellow]*WATCH* Moderate EBITDA margin[/]"
    if val < 0.45:
        return "[green]*OK* Strong EBITDA margin[/]"
    return "[bold green]*STRONG* Excellent — high operating leverage[/]"


# --- Solvency assessments ---

def _a_de(val):
    if _isna(val):
        return "[dim]No debt/equity data[/]"
    if val < 0:
        return "[red]*CRITICAL* Negative equity — liabilities exceed assets[/]"
    if val == 0:
        return "[bold green]*STRONG* No debt — clean balance sheet[/]"
    if val < 0.20:
        return "[green]*OK* Very low leverage — conservative financing[/]"
    if val < 0.50:
        return "[green]*OK* Moderate leverage — manageable for energy companies[/]"
    if val < 1.00:
        return "[yellow]*WATCH* Elevated leverage — monitor debt service[/]"
    if val < 2.00:
        return "[#ff8800]*WARNING* High leverage — risky for cyclical business[/]"
    return "[bold red]*CRITICAL* Very high leverage — distress risk in downturns[/]"


def _a_cr(val):
    if _isna(val):
        return "[dim]No current ratio data[/]"
    if val > 5.0:
        return "[green]*OK* Very liquid — may be under-deploying capital[/]"
    if val > 3.0:
        return "[green]*OK* Very strong liquidity position[/]"
    if val > 2.0:
        return "[green]*OK* Strong — comfortable short-term coverage[/]"
    if val > 1.5:
        return "[yellow]*WATCH* Adequate liquidity[/]"
    if val > 1.0:
        return "[#ff8800]*WARNING* Tight — short-term obligations near current assets[/]"
    return "[bold red]*CRITICAL* Liquidity risk — current liabilities exceed assets[/]"


def _a_qr(val):
    if _isna(val):
        return "[dim]No quick ratio data[/]"
    if val > 3.0:
        return "[green]*OK* Very strong quick ratio[/]"
    if val > 1.5:
        return "[green]*OK* Good — liquid assets cover near-term obligations[/]"
    if val > 1.0:
        return "[yellow]*WATCH* Adequate without relying on inventory[/]"
    if val > 0.5:
        return "[#ff8800]*WARNING* Needs inventory liquidation to meet obligations[/]"
    return "[red]*CRITICAL* Weak — immediate liquidity concern[/]"


def _a_ic(val):
    if _isna(val):
        return "[dim]No interest coverage data[/]"
    if val < 0:
        return "[red]*CRITICAL* Negative — not covering interest from operations[/]"
    if val < 1.5:
        return "[bold red]*CRITICAL* Dangerously low — default risk[/]"
    if val < 3.0:
        return "[#ff8800]*WARNING* Thin coverage — vulnerable in downturns[/]"
    if val < 6.0:
        return "[yellow]*WATCH* Adequate interest coverage[/]"
    if val < 12.0:
        return "[green]*OK* Comfortable — well-covered[/]"
    return "[bold green]*STRONG* Very strong — interest is trivial[/]"


def _a_burn(val):
    if _isna(val):
        return "[dim]No burn rate data[/]"
    if val == 0:
        return "[green]*OK* Not burning cash — break-even or profitable[/]"
    if val > 0:
        return "[green]*OK* Cash flow positive — generating cash[/]"
    abv = abs(val)
    if abv < 2_000_000:
        return f"[yellow]*WATCH* Modest burn — {fmt_money(abv)}/yr[/]"
    if abv < 10_000_000:
        return f"[#ff8800]*WARNING* Significant burn — {fmt_money(abv)}/yr[/]"
    return f"[bold red]*CRITICAL* Heavy burn — {fmt_money(abv)}/yr — financing needed[/]"


def _a_runway(val):
    if _isna(val):
        return "[dim]No runway data — could be cash-positive[/]"
    if val > 5.0:
        return "[bold green]*STRONG* Excellent — 5+ years runway, minimal dilution pressure[/]"
    if val > 3.0:
        return "[green]*OK* Comfortable — time to reach milestones[/]"
    if val > 1.5:
        return "[yellow]*WATCH* Adequate — monitor quarterly for changes[/]"
    if val > 0.75:
        return "[#ff8800]*WARNING* Tight — financing discussions likely underway[/]"
    if val > 0:
        return "[bold red]*CRITICAL* Critical — fundraising imminent, expect dilution[/]"
    return "[bold red]*CRITICAL* Cash depleted — emergency funding needed[/]"


def _a_burn_pct(val):
    if _isna(val):
        return "[dim]No burn/market cap data[/]"
    if val > 0.15:
        return "[bold red]*CRITICAL* Extreme burn >15% of market cap — unsustainable[/]"
    if val > 0.08:
        return "[red]*WARNING* High burn >8% — significant annual value erosion[/]"
    if val > 0.04:
        return "[yellow]*WATCH* Moderate burn — 4-8% of market cap consumed yearly[/]"
    if val > 0.02:
        return "[green]*OK* Low burn rate relative to market cap[/]"
    return "[green]*OK* Minimal burn — negligible market cap impact[/]"


def _a_wc(val):
    if _isna(val):
        return "[dim]No working capital data[/]"
    if val < 0:
        return "[bold red]*CRITICAL* Negative working capital — near-term funding gap[/]"
    if val < 1_000_000:
        return "[#ff8800]*WARNING* Thin working capital cushion[/]"
    if val < 10_000_000:
        return "[yellow]*WATCH* Moderate working capital[/]"
    return "[green]*OK* Strong working capital position[/]"


def _a_cps(val):
    if _isna(val):
        return "[dim]No cash per share data[/]"
    return f"[cyan]Cash floor reference: ${val:.2f}/share[/]"


def _a_ncavps(val):
    if val is None:
        return "[dim]No NCAV per share data[/]"
    if val < 0:
        return "[red]*WARNING* Negative NCAV — net liabilities exceed current assets[/]"
    return f"[cyan]*OK* Liquidation floor: ${val:.4f}/share[/]"


# --- Growth assessments ---

def _a_revg(val):
    if _isna(val):
        return "[dim]No revenue growth — pre-production stage[/]"
    if val > 0.50:
        return "[bold green]*STRONG* Exceptional revenue growth >50%[/]"
    if val > 0.20:
        return "[green]*OK* Strong revenue growth[/]"
    if val > 0.05:
        return "[yellow]*WATCH* Modest growth[/]"
    if val > -0.05:
        return "[dim]Flat revenue[/]"
    if val > -0.20:
        return "[#ff8800]*WARNING* Revenue declining — check commodity prices[/]"
    return "[red]*CRITICAL* Significant revenue decline[/]"


def _a_revcagr(val):
    if _isna(val):
        return "[dim]No 3-year revenue CAGR[/]"
    if val > 0.25:
        return "[bold green]*STRONG* Strong multi-year revenue CAGR[/]"
    if val > 0.10:
        return "[green]*OK* Solid revenue growth trajectory[/]"
    if val > 0:
        return "[yellow]*WATCH* Modest growth trend[/]"
    return "[#ff8800]*WARNING* Revenue contracting over 3 years[/]"


def _a_earng(val):
    if _isna(val):
        return "[dim]No earnings growth data[/]"
    if val > 0.50:
        return "[bold green]*STRONG* Earnings surging — verify sustainability[/]"
    if val > 0.15:
        return "[green]*OK* Strong earnings improvement[/]"
    if val > 0:
        return "[yellow]*WATCH* Modest earnings growth[/]"
    if val > -0.20:
        return "[#ff8800]*WARNING* Earnings declining[/]"
    return "[red]*CRITICAL* Significant earnings deterioration[/]"


def _a_bvg(val):
    if _isna(val):
        return "[dim]No book value growth data[/]"
    if val > 0.15:
        return "[bold green]*STRONG* Book value growing rapidly — reinvesting well[/]"
    if val > 0.05:
        return "[green]*OK* Book value increasing — capital accumulation[/]"
    if val > -0.03:
        return "[yellow]*WATCH* Book value roughly flat[/]"
    if val > -0.15:
        return "[#ff8800]*WARNING* Book value eroding — losses or impairments[/]"
    return "[red]*CRITICAL* Significant book value destruction[/]"


def _a_fcfg(val):
    if _isna(val):
        return "[dim]No FCF growth data[/]"
    if val > 0.30:
        return "[bold green]*STRONG* FCF growth accelerating[/]"
    if val > 0.10:
        return "[green]*OK* Growing free cash flow[/]"
    if val > -0.10:
        return "[yellow]*WATCH* FCF roughly stable[/]"
    return "[#ff8800]*WARNING* FCF declining — capex cycle or margin compression[/]"


def _a_dil(val):
    if _isna(val):
        return "[dim]No dilution data[/]"
    if val < -0.05:
        return "[bold green]*STRONG* Meaningful buybacks — shareholder friendly[/]"
    if val < -0.01:
        return "[bold green]*STRONG* Minor share buybacks[/]"
    if val < 0.02:
        return "[green]*OK* Minimal dilution — tight share structure[/]"
    if val < 0.05:
        return "[yellow]*WATCH* Modest dilution — typical for funded explorers[/]"
    if val < 0.10:
        return "[#ff8800]*WARNING* Significant dilution (5-10%/yr) — equity raises[/]"
    if val < 0.20:
        return "[red]*WARNING* Heavy dilution (10-20%/yr) — aggressive financing[/]"
    return "[bold red]*CRITICAL* Extreme dilution >20%/yr — value destruction[/]"


def _a_dil3y(val):
    if _isna(val):
        return "[dim]No 3-year dilution CAGR[/]"
    if val < 0:
        return "[green]*OK* Share count shrinking — buyback program[/]"
    if val < 0.03:
        return "[green]*OK* Minimal cumulative dilution over 3 years[/]"
    if val < 0.08:
        return "[yellow]*WATCH* Moderate 3-year dilution — ongoing equity raises[/]"
    if val < 0.15:
        return "[#ff8800]*WARNING* High 3-year dilution CAGR — persistent fundraising[/]"
    return "[bold red]*CRITICAL* Chronic heavy dilution — structural financing issue[/]"


# --- Share structure assessments ---

def _a_shares_out(val):
    if _isna(val):
        return "[dim]No share count data[/]"
    if val > 1_000_000_000:
        return "[red]*CRITICAL* Over 1B shares — heavily diluted, limits upside per share[/]"
    if val > 500_000_000:
        return "[#ff8800]*WARNING* Large float >500M — significant past dilution[/]"
    if val > 200_000_000:
        return "[yellow]*WATCH* Moderate share count[/]"
    if val > 50_000_000:
        return "[green]*OK* Reasonable share count — manageable structure[/]"
    return "[bold green]*STRONG* Tight share count — high torque to price[/]"


def _a_fd_shares(val):
    if _isna(val):
        return "[dim]No fully diluted count[/]"
    if val > 1_500_000_000:
        return "[red]*CRITICAL* Very high fully diluted count — warrant/option overhang[/]"
    if val > 500_000_000:
        return "[#ff8800]*WARNING* Large diluted count — significant overhang risk[/]"
    if val > 200_000_000:
        return "[yellow]*WATCH* Moderate diluted share base[/]"
    return "[green]*OK* Tight diluted share base[/]"


def _a_insider(val):
    if _isna(val):
        return "[dim]No insider ownership data[/]"
    if val > 0.30:
        return "[bold green]*STRONG* Very high insider ownership — strong alignment[/]"
    if val > 0.15:
        return "[green]*OK* Solid insider ownership — skin in the game[/]"
    if val > 0.05:
        return "[yellow]*WATCH* Moderate insider ownership[/]"
    if val > 0.01:
        return "[#ff8800]*WARNING* Low insider ownership — limited alignment[/]"
    return "[red]*CRITICAL* Minimal insider ownership — check for pay-to-play[/]"


def _a_inst(val):
    if _isna(val):
        return "[dim]No institutional ownership data[/]"
    if val > 0.60:
        return "[green]*OK* High institutional — validates investment thesis[/]"
    if val > 0.30:
        return "[green]*OK* Good institutional backing[/]"
    if val > 0.10:
        return "[yellow]*WATCH* Some institutional interest[/]"
    return "[dim]Low institutional — under-followed, potential discovery[/]"


def _a_ss_assessment(val):
    if not val:
        return "[dim]No assessment available[/]"
    return val


# --- Energy-specific metric assessments ---

def _a_fcf_yield(val):
    if _isna(val):
        return "[dim]No FCF yield data[/]"
    if val > 0.12:
        return "[bold green]*STRONG* Excellent FCF yield >12% — strong cash generation[/]"
    if val > 0.08:
        return "[green]*OK* Good FCF yield 8-12% — solid cash returns[/]"
    if val > 0.05:
        return "[yellow]*WATCH* Moderate FCF yield 5-8%[/]"
    if val > 0.02:
        return "[#ff8800]*WARNING* Low FCF yield <5% — limited cash return[/]"
    if val > 0:
        return "[red]*CRITICAL* Very low FCF yield — reinvesting most cash flow[/]"
    return "[red]*CRITICAL* Negative FCF yield — cash consuming[/]"


def _a_croci(val):
    if _isna(val):
        return "[dim]No CROCI data[/]"
    if val > 0.20:
        return "[bold green]*STRONG* Exceptional cash returns on capital >20%[/]"
    if val > 0.12:
        return "[green]*OK* Good CROCI — generating solid cash returns[/]"
    if val > 0.06:
        return "[yellow]*WATCH* Moderate CROCI — near cost of capital[/]"
    if val > 0:
        return "[#ff8800]*WARNING* Low CROCI — below cost of capital[/]"
    return "[red]*CRITICAL* Negative CROCI — destroying cash value[/]"


def _a_ocf_ni(val):
    if _isna(val):
        return "[dim]No data[/]"
    if val > 1.5:
        return "[bold green]*STRONG* Cash flow well exceeds earnings — high quality[/]"
    if val > 1.0:
        return "[green]*OK* Cash flow exceeds earnings — good quality[/]"
    if val > 0.7:
        return "[yellow]*WATCH* Cash flow slightly below earnings[/]"
    if val > 0:
        return "[#ff8800]*WARNING* Earnings exceeding cash flow — check accruals[/]"
    return "[red]*CRITICAL* Negative OCF despite reported earnings — red flag[/]"


def _a_debt_ps(val):
    if _isna(val):
        return "[dim]No debt per share data[/]"
    return f"[cyan]Debt burden: ${val:.2f}/share[/]"


def _a_dsc(val):
    if _isna(val):
        return "[dim]No debt service data[/]"
    if val > 8:
        return "[bold green]*STRONG* Very strong debt service coverage[/]"
    if val > 4:
        return "[green]*OK* Comfortable — well covered[/]"
    if val > 2:
        return "[yellow]*WATCH* Adequate but monitor[/]"
    if val > 1:
        return "[#ff8800]*WARNING* Tight debt service — vulnerable in downturn[/]"
    return "[red]*CRITICAL* Cannot cover debt service from operations[/]"


def _a_capex_rev(val):
    if _isna(val):
        return "[dim]No capex/revenue data[/]"
    if val > 0.50:
        return "[red]*CRITICAL* Capex >50% of revenue — extreme capital intensity[/]"
    if val > 0.35:
        return "[#ff8800]*WARNING* High capex intensity 35-50% — heavy reinvestment[/]"
    if val > 0.20:
        return "[yellow]*WATCH* Moderate capex 20-35% — typical for E&P[/]"
    if val > 0.10:
        return "[green]*OK* Disciplined capex 10-20%[/]"
    return "[bold green]*STRONG* Very low capex intensity <10% — capital light[/]"


def _a_capex_ocf(val):
    if _isna(val):
        return "[dim]No capex/OCF data[/]"
    if val > 1.0:
        return "[red]*CRITICAL* Capex exceeds operating cash flow — unsustainable[/]"
    if val > 0.80:
        return "[#ff8800]*WARNING* Capex consuming >80% of OCF — limited FCF[/]"
    if val > 0.60:
        return "[yellow]*WATCH* Capex at 60-80% of OCF — growth phase[/]"
    if val > 0.40:
        return "[green]*OK* Balanced capex/OCF ratio 40-60%[/]"
    return "[bold green]*STRONG* Low capex intensity — strong FCF conversion[/]"


def _a_reinvestment(val):
    if _isna(val):
        return "[dim]No reinvestment data[/]"
    if val > 1.0:
        return "[red]*CRITICAL* Reinvesting more than EBITDA — external funding needed[/]"
    if val > 0.70:
        return "[#ff8800]*WARNING* High reinvestment >70% — limited shareholder returns[/]"
    if val > 0.50:
        return "[yellow]*WATCH* Moderate reinvestment 50-70%[/]"
    if val > 0.30:
        return "[green]*OK* Disciplined reinvestment 30-50%[/]"
    return "[bold green]*STRONG* Low reinvestment — harvesting mode[/]"


def _a_div_payout(val):
    if _isna(val):
        return "[dim]No dividend payout data[/]"
    if val > 1.0:
        return "[red]*CRITICAL* Paying more than 100% of earnings — unsustainable[/]"
    if val > 0.80:
        return "[#ff8800]*WARNING* Payout >80% — limited safety margin[/]"
    if val > 0.60:
        return "[yellow]*WATCH* Moderate payout 60-80%[/]"
    if val > 0.30:
        return "[green]*OK* Sustainable payout 30-60%[/]"
    return "[bold green]*STRONG* Conservative payout <30% — room for growth[/]"


def _a_div_cover(val):
    if _isna(val):
        return "[dim]No dividend coverage data[/]"
    if val > 3.0:
        return "[bold green]*STRONG* FCF covers dividend 3x+ — very safe[/]"
    if val > 2.0:
        return "[green]*OK* FCF covers dividend 2x+ — solid[/]"
    if val > 1.2:
        return "[yellow]*WATCH* FCF covers dividend but tight margin[/]"
    if val > 1.0:
        return "[#ff8800]*WARNING* Barely covered by FCF — at risk[/]"
    return "[red]*CRITICAL* FCF does not cover dividend — cut risk[/]"


def _a_shareholder_yield(val):
    if _isna(val):
        return "[dim]No shareholder yield data[/]"
    if val > 0.10:
        return "[bold green]*STRONG* Total shareholder yield >10% — exceptional[/]"
    if val > 0.06:
        return "[green]*OK* Good shareholder yield 6-10%[/]"
    if val > 0.03:
        return "[yellow]*WATCH* Moderate shareholder yield 3-6%[/]"
    if val > 0:
        return "[dim]*OK* Low but positive shareholder yield[/]"
    return "[dim]No shareholder returns[/]"


def _a_fcf_ps(val):
    if _isna(val):
        return "[dim]No FCF per share data[/]"
    if val > 0:
        return f"[green]*OK* FCF per share: ${val:.2f}[/]"
    return f"[red]*WARNING* Negative FCF per share: ${val:.2f}[/]"


def _a_ocf_ps(val):
    if _isna(val):
        return "[dim]No OCF per share data[/]"
    if val > 0:
        return f"[green]*OK* Operating cash flow: ${val:.2f}/share[/]"
    return f"[red]*WARNING* Negative OCF: ${val:.2f}/share[/]"


def _a_fcf_conv(val):
    if _isna(val):
        return "[dim]No FCF conversion data[/]"
    if val > 0.60:
        return "[bold green]*STRONG* Excellent FCF/EBITDA conversion >60%[/]"
    if val > 0.40:
        return "[green]*OK* Good FCF conversion 40-60%[/]"
    if val > 0.20:
        return "[yellow]*WATCH* Moderate FCF conversion 20-40%[/]"
    if val > 0:
        return "[#ff8800]*WARNING* Low FCF conversion — heavy capex or working capital[/]"
    return "[red]*CRITICAL* Negative FCF conversion[/]"


def _a_capex_int(val):
    if _isna(val):
        return "[dim]No capex intensity data[/]"
    if val > 0.40:
        return "[red]*CRITICAL* Very high capex intensity >40%[/]"
    if val > 0.25:
        return "[#ff8800]*WARNING* High capex intensity 25-40%[/]"
    if val > 0.15:
        return "[yellow]*WATCH* Moderate capex intensity 15-25%[/]"
    if val > 0.08:
        return "[green]*OK* Disciplined capex intensity[/]"
    return "[bold green]*STRONG* Very low capex intensity — capital efficient[/]"


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def display_full_report(report):
    """Render the complete analysis report to the console."""
    _display_header(report)
    _display_profile(report)
    if report.valuation:
        _display_valuation(report)
    if report.profitability:
        _display_profitability(report)
    if report.solvency:
        _display_solvency(report)
    if report.growth:
        _display_growth(report)
    if report.share_structure:
        _display_share_structure(report)
    if report.energy_quality:
        _display_energy_quality(report)
    if report.intrinsic_value:
        _display_intrinsic_value(report)
    if report.market_intelligence:
        _display_market_intelligence(report)
    _display_financials(report)
    _display_filings(report)
    _display_news(report)
    if report.valuation:
        _display_conclusion(report)
    console.print()


_progressive_stages_seen: set[str] = set()


def display_report_stage(stage, report):
    """Render a single analysis stage (used in progressive display)."""
    global _progressive_stages_seen
    handlers = {
        "profile": lambda: (
            _progressive_stages_seen.clear(),
            _progressive_stages_seen.add("profile"),
            _display_header(report),
            _display_profile(report),
        ),
        "financials": lambda: (
            _progressive_stages_seen.add("financials"),
            _display_financials(report),
        ),
        "valuation": lambda: (
            _progressive_stages_seen.add("valuation"),
            _display_valuation(report),
        ),
        "profitability": lambda: (
            _progressive_stages_seen.add("profitability"),
            _display_profitability(report),
        ),
        "solvency": lambda: (
            _progressive_stages_seen.add("solvency"),
            _display_solvency(report),
        ),
        "growth": lambda: (
            _progressive_stages_seen.add("growth"),
            _display_growth(report),
        ),
        "share_structure": lambda: (
            _progressive_stages_seen.add("share_structure"),
            _display_share_structure(report),
        ),
        "energy_quality": lambda: (
            _progressive_stages_seen.add("energy_quality"),
            _display_energy_quality(report),
        ),
        "intrinsic_value": lambda: (
            _progressive_stages_seen.add("intrinsic_value"),
            _display_intrinsic_value(report),
        ),
        "market_intelligence": lambda: (
            _progressive_stages_seen.add("market_intelligence"),
            _display_market_intelligence(report),
        ),
        "filings": lambda: (
            _progressive_stages_seen.add("filings"),
            _display_filings(report),
        ),
        "news": lambda: (
            _progressive_stages_seen.add("news"),
            _display_news(report),
        ),
        "conclusion": lambda: (
            _progressive_stages_seen.add("conclusion"),
            _display_conclusion(report),
        ),
    }
    if stage in handlers:
        handlers[stage]()
    elif stage == "complete":
        if not _progressive_stages_seen:
            display_full_report(report)
        else:
            console.print()
        _progressive_stages_seen.clear()


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def _display_header(report):
    p = report.profile
    header = Text()
    header.append(f"  {p.name}", style="bold white on blue")
    header.append(f"  ({p.ticker})", style="bold cyan on blue")
    if p.isin:
        header.append(f"  ISIN: {p.isin}", style="dim on blue")
    console.print(Panel(
        header,
        title="[bold]LYNX Energy Analysis[/]",
        border_style="blue",
    ))
    tc = _tier_color(p.tier)
    sc = _stage_color(p.stage)
    console.print(Panel(
        f"[{tc}]{p.tier.value}[/]  |  [{sc}]{p.stage.value}[/]\n"
        f"[cyan]Commodity:[/] {p.primary_commodity.value}  |  "
        f"[cyan]Jurisdiction:[/] {p.jurisdiction_tier.value}\n"
        f"[dim]* = critical metric for this stage/tier  |  dimmed = less relevant[/]",
        border_style=tc,
        title=f"[{tc}]{p.tier.value}[/] [{sc}]{p.stage.value}[/]",
    ))


def _display_profile(report):
    p = report.profile
    t = Table(show_header=False, box=None, padding=(0, 2))
    t.add_column("Key", style="bold")
    t.add_column("Value")
    t.add_row("Sector", p.sector or "N/A")
    t.add_row("Industry", p.industry or "N/A")
    t.add_row("Country", p.country or "N/A")
    t.add_row("Exchange", p.exchange or "N/A")
    t.add_row("Market Cap", fmt_money(p.market_cap))
    t.add_row("Employees", f"{p.employees:,}" if p.employees else "N/A")
    t.add_row("Website", p.website or "N/A")
    console.print(Panel(t, title="[bold]Company Profile[/]", border_style="cyan"))
    if p.description:
        desc = p.description[:800] + ("..." if len(p.description) > 800 else "")
        console.print(Panel(desc, title="[bold]Business Description[/]", border_style="dim"))
    try:
        from lynx_energy.metrics.sector_insights import get_sector_insight, get_industry_insight
        si = get_sector_insight(p.sector)
        if si:
            st = Table(show_header=False, box=None, padding=(0, 1))
            st.add_column("Key", style="bold cyan", min_width=20, no_wrap=True)
            st.add_column("Value", ratio=1, overflow="fold")
            st.add_row("Overview", si.overview)
            st.add_row("Critical Metrics", ", ".join(si.critical_metrics))
            st.add_row("Key Risks", ", ".join(si.key_risks))
            st.add_row("What to Watch", ", ".join(si.what_to_watch))
            st.add_row("Typical Valuation", si.typical_valuation)
            console.print(Panel(
                st,
                title=f"[bold]Sector: {si.sector}[/]",
                border_style="blue",
            ))
        ii = get_industry_insight(p.industry)
        if ii:
            it = Table(show_header=False, box=None, padding=(0, 1))
            it.add_column("Key", style="bold cyan", min_width=20, no_wrap=True)
            it.add_column("Value", ratio=1, overflow="fold")
            it.add_row("Overview", ii.overview)
            it.add_row("Critical Metrics", ", ".join(ii.critical_metrics))
            it.add_row("Key Risks", ", ".join(ii.key_risks))
            it.add_row("What to Watch", ", ".join(ii.what_to_watch))
            it.add_row("Typical Valuation", ii.typical_valuation)
            console.print(Panel(
                it,
                title=f"[bold]Industry: {ii.industry}[/]",
                border_style="blue",
            ))
    except ImportError:
        pass


def _display_valuation(report):
    """Valuation metrics — all rows use get_relevance with tier AND stage."""
    v = report.valuation
    if v is None:
        return
    tier, stage = report.profile.tier, report.profile.stage
    rel = lambda key: get_relevance(key, tier, "valuation", stage)

    t = Table(title="Valuation Metrics", show_lines=True, border_style="yellow")
    t.add_column("Metric", style="bold", min_width=22, no_wrap=True)
    t.add_column("Value", justify="right", min_width=14, no_wrap=True)
    t.add_column("Assessment", ratio=1, overflow="fold")

    _add_metric_row(t, "P/E (Trailing)", fmt_num(v.pe_trailing),
                    _a_pe(v.pe_trailing), rel("pe_trailing"))
    _add_metric_row(t, "P/B Ratio", fmt_num(v.pb_ratio),
                    _a_pb(v.pb_ratio), rel("pb_ratio"))
    _add_metric_row(t, "P/S Ratio", fmt_num(v.ps_ratio),
                    _a_ps(v.ps_ratio), rel("ps_ratio"))
    _add_metric_row(t, "P/FCF", fmt_num(v.p_fcf),
                    _a_pfcf(v.p_fcf), rel("p_fcf"))
    _add_metric_row(t, "EV/EBITDA", fmt_num(v.ev_ebitda),
                    _a_ev(v.ev_ebitda), rel("ev_ebitda"))
    _add_metric_row(t, "EV/Revenue", fmt_num(v.ev_revenue),
                    _a_evrev(v.ev_revenue), rel("ev_revenue"))
    _add_metric_row(t, "PEG Ratio", fmt_num(v.peg_ratio),
                    _a_peg(v.peg_ratio), rel("peg_ratio"))
    _add_metric_row(t, "Earnings Yield", fmt_pct(v.earnings_yield),
                    _a_ey(v.earnings_yield), rel("earnings_yield"))
    _add_metric_row(t, "Dividend Yield", fmt_pct(v.dividend_yield),
                    _a_divy(v.dividend_yield), rel("dividend_yield"))
    _add_metric_row(t, "P/Tangible Book", fmt_num(v.price_to_tangible_book),
                    _a_ptb(v.price_to_tangible_book), rel("price_to_tangible_book"))
    _add_metric_row(t, "P/NCAV (Net-Net)", fmt_num(v.price_to_ncav),
                    _a_pncav(v.price_to_ncav), rel("price_to_ncav"))
    _add_metric_row(t, "Cash/Market Cap", fmt_pct(v.cash_to_market_cap),
                    _a_ctm(v.cash_to_market_cap), rel("cash_to_market_cap"))
    _add_metric_row(t, "FCF Yield", fmt_pct(v.fcf_yield),
                    _a_fcf_yield(v.fcf_yield), rel("fcf_yield"))
    console.print(t)


def _display_profitability(report):
    """Profitability metrics — all rows use get_relevance with tier AND stage."""
    p = report.profitability
    if p is None:
        return
    tier, stage = report.profile.tier, report.profile.stage
    rel = lambda key: get_relevance(key, tier, "profitability", stage)

    _keys = ["roe", "roa", "roic", "gross_margin", "operating_margin", "net_margin", "fcf_margin", "ebitda_margin"]
    all_irrelevant = all(rel(k) == Relevance.IRRELEVANT for k in _keys)

    t = Table(title="Profitability Metrics", show_lines=True, border_style="green")
    t.add_column("Metric", style="bold", min_width=22, no_wrap=True)
    t.add_column("Value", justify="right", min_width=14, no_wrap=True)
    t.add_column("Assessment", ratio=1, overflow="fold")

    if all_irrelevant:
        stage_name = report.profile.stage.value if hasattr(report.profile.stage, "value") else str(report.profile.stage)
        t.add_row(
            "[dim]  N/A[/]",
            "[dim]--[/]",
            f"[dim]Profitability metrics are not applicable for {stage_name} stage companies. "
            f"Pre-revenue energy companies have no meaningful margins or returns on capital to evaluate.[/]",
        )
    else:
        _add_metric_row(t, "ROE", fmt_pct(p.roe),
                        _a_roe(p.roe), rel("roe"))
        _add_metric_row(t, "ROA", fmt_pct(p.roa),
                        _a_roa(p.roa), rel("roa"))
        _add_metric_row(t, "ROIC", fmt_pct(p.roic),
                        _a_roic(p.roic), rel("roic"))
        _add_metric_row(t, "Gross Margin", fmt_pct(p.gross_margin),
                        _a_gm(p.gross_margin), rel("gross_margin"))
        _add_metric_row(t, "Operating Margin", fmt_pct(p.operating_margin),
                        _a_om(p.operating_margin), rel("operating_margin"))
        _add_metric_row(t, "Net Margin", fmt_pct(p.net_margin),
                        _a_nm(p.net_margin), rel("net_margin"))
        _add_metric_row(t, "FCF Margin", fmt_pct(p.fcf_margin),
                        _a_fcfm(p.fcf_margin), rel("fcf_margin"))
        _add_metric_row(t, "EBITDA Margin", fmt_pct(p.ebitda_margin),
                        _a_ebitdam(p.ebitda_margin), rel("ebitda_margin"))
        _add_metric_row(t, "CROCI", fmt_pct(p.croci),
                        _a_croci(p.croci), rel("croci"))
        _add_metric_row(t, "OCF/Net Income", fmt_num(p.ocf_to_net_income),
                        _a_ocf_ni(p.ocf_to_net_income), rel("ocf_to_net_income"))
    console.print(t)


def _display_solvency(report):
    """Solvency metrics — all rows use get_relevance with tier AND stage."""
    s = report.solvency
    if s is None:
        return
    tier, stage = report.profile.tier, report.profile.stage
    rel = lambda key: get_relevance(key, tier, "solvency", stage)

    title = "Survival & Financial Health" if tier in (CompanyTier.MICRO, CompanyTier.NANO) else "Solvency & Financial Health"
    t = Table(title=title, show_lines=True, border_style="red")
    t.add_column("Metric", style="bold", min_width=22, no_wrap=True)
    t.add_column("Value", justify="right", min_width=14, no_wrap=True)
    t.add_column("Assessment", ratio=1, overflow="fold")

    _add_metric_row(t, "Debt/Equity", fmt_num(s.debt_to_equity),
                    _a_de(s.debt_to_equity), rel("debt_to_equity"))
    _add_metric_row(t, "Current Ratio", fmt_num(s.current_ratio),
                    _a_cr(s.current_ratio), rel("current_ratio"))
    _add_metric_row(t, "Quick Ratio", fmt_num(s.quick_ratio),
                    _a_qr(s.quick_ratio), rel("quick_ratio"))
    _add_metric_row(t, "Interest Coverage", fmt_num(s.interest_coverage, 1),
                    _a_ic(s.interest_coverage), rel("interest_coverage"))
    _add_metric_row(t, "Cash Burn Rate (/yr)", fmt_money(s.cash_burn_rate),
                    _a_burn(s.cash_burn_rate), rel("cash_burn_rate"))
    _add_metric_row(t, "Cash Runway",
                    f"{s.cash_runway_years:.1f} years" if s.cash_runway_years else "[dim]N/A[/]",
                    _a_runway(s.cash_runway_years), rel("cash_runway_years"))
    _add_metric_row(t, "Burn % of Mkt Cap", fmt_pct(s.burn_as_pct_of_market_cap),
                    _a_burn_pct(s.burn_as_pct_of_market_cap), rel("burn_as_pct_of_market_cap"))
    _add_metric_row(t, "Working Capital", fmt_money(s.working_capital),
                    _a_wc(s.working_capital), rel("working_capital"))
    _add_metric_row(t, "Cash Per Share",
                    f"${s.cash_per_share:.2f}" if s.cash_per_share else "[dim]N/A[/]",
                    _a_cps(s.cash_per_share), rel("cash_per_share"))
    _add_metric_row(t, "NCAV Per Share",
                    f"${s.ncav_per_share:.4f}" if s.ncav_per_share is not None else "[dim]N/A[/]",
                    _a_ncavps(s.ncav_per_share), rel("ncav_per_share"))
    _add_metric_row(t, "Total Cash", fmt_money(s.total_cash),
                    "[cyan]Cash on hand[/]" if not _isna(s.total_cash) else "[dim]No data[/]",
                    rel("total_cash") if hasattr(s, 'total_cash') else Relevance.RELEVANT)
    _add_metric_row(t, "Total Debt", fmt_money(s.total_debt),
                    _a_debt_total(s.total_debt),
                    rel("total_debt") if hasattr(s, 'total_debt') else Relevance.RELEVANT)
    _add_metric_row(t, "Net Debt", fmt_money(s.net_debt),
                    _a_net_debt(s.net_debt),
                    rel("net_debt") if hasattr(s, 'net_debt') else Relevance.RELEVANT)
    _add_metric_row(t, "Debt Per Share",
                    f"${s.debt_per_share:.2f}" if s.debt_per_share is not None else "[dim]N/A[/]",
                    _a_debt_ps(s.debt_per_share), rel("debt_per_share"))
    _add_metric_row(t, "Debt Service Coverage", fmt_num(s.debt_service_coverage, 1),
                    _a_dsc(s.debt_service_coverage), rel("debt_service_coverage"))
    console.print(t)


def _a_debt_total(val):
    if _isna(val):
        return "[dim]No debt data[/]"
    if val == 0:
        return "[bold green]*STRONG* Debt-free balance sheet[/]"
    return f"[cyan]Total obligations: {fmt_money(val)}[/]"


def _a_net_debt(val):
    if _isna(val):
        return "[dim]No net debt data[/]"
    if val < 0:
        return "[green]*OK* Net cash position — cash exceeds debt[/]"
    if val == 0:
        return "[yellow]*WATCH* Break-even — cash equals debt[/]"
    return "[#ff8800]*WARNING* Net debt — leverage present[/]"


def _display_growth(report):
    """Growth & dilution metrics — all rows use get_relevance with tier AND stage."""
    g = report.growth
    if g is None:
        return
    tier, stage = report.profile.tier, report.profile.stage
    rel = lambda key: get_relevance(key, tier, "growth", stage)

    t = Table(title="Growth & Dilution Metrics", show_lines=True, border_style="magenta")
    t.add_column("Metric", style="bold", min_width=22, no_wrap=True)
    t.add_column("Value", justify="right", min_width=14, no_wrap=True)
    t.add_column("Assessment", ratio=1, overflow="fold")

    _add_metric_row(t, "Revenue Growth (YoY)", fmt_pct(g.revenue_growth_yoy),
                    _a_revg(g.revenue_growth_yoy), rel("revenue_growth_yoy"))
    _add_metric_row(t, "Revenue CAGR (3Y)", fmt_pct(g.revenue_cagr_3y),
                    _a_revcagr(g.revenue_cagr_3y), rel("revenue_cagr_3y"))
    _add_metric_row(t, "Earnings Growth (YoY)", fmt_pct(g.earnings_growth_yoy),
                    _a_earng(g.earnings_growth_yoy), rel("earnings_growth_yoy"))
    _add_metric_row(t, "Book Value Growth (YoY)", fmt_pct(g.book_value_growth_yoy),
                    _a_bvg(g.book_value_growth_yoy), rel("book_value_growth_yoy"))
    _add_metric_row(t, "FCF Growth (YoY)", fmt_pct(g.fcf_growth_yoy),
                    _a_fcfg(g.fcf_growth_yoy), rel("fcf_growth_yoy"))
    _add_metric_row(t, "Share Dilution (YoY)", fmt_pct(g.shares_growth_yoy),
                    _a_dil(g.shares_growth_yoy), rel("shares_growth_yoy"))
    _add_metric_row(t, "Dilution CAGR (3Y)", fmt_pct(g.shares_growth_3y_cagr),
                    _a_dil3y(g.shares_growth_3y_cagr), rel("shares_growth_3y_cagr"))
    _add_metric_row(t, "Capex/Revenue", fmt_pct(g.capex_to_revenue),
                    _a_capex_rev(g.capex_to_revenue), rel("capex_to_revenue"))
    _add_metric_row(t, "Capex/OCF", fmt_pct(g.capex_to_ocf),
                    _a_capex_ocf(g.capex_to_ocf), rel("capex_to_ocf"))
    _add_metric_row(t, "Reinvestment Rate", fmt_pct(g.reinvestment_rate),
                    _a_reinvestment(g.reinvestment_rate), rel("reinvestment_rate"))
    _add_metric_row(t, "Div. Payout Ratio", fmt_pct(g.dividend_payout_ratio),
                    _a_div_payout(g.dividend_payout_ratio), rel("dividend_payout_ratio"))
    _add_metric_row(t, "Div. Coverage (FCF)", fmt_num(g.dividend_coverage, 1),
                    _a_div_cover(g.dividend_coverage), rel("dividend_coverage"))
    _add_metric_row(t, "Shareholder Yield", fmt_pct(g.shareholder_yield),
                    _a_shareholder_yield(g.shareholder_yield), rel("shareholder_yield"))
    _add_metric_row(t, "FCF Per Share",
                    f"${g.fcf_per_share:.2f}" if g.fcf_per_share is not None else "[dim]N/A[/]",
                    _a_fcf_ps(g.fcf_per_share), rel("fcf_per_share"))
    _add_metric_row(t, "OCF Per Share",
                    f"${g.ocf_per_share:.2f}" if g.ocf_per_share is not None else "[dim]N/A[/]",
                    _a_ocf_ps(g.ocf_per_share), rel("ocf_per_share"))
    console.print(t)


def _display_share_structure(report):
    """Share structure — uses relevance markers via get_relevance with category='share_structure'."""
    ss = report.share_structure
    if ss is None:
        return
    tier, stage = report.profile.tier, report.profile.stage
    rel = lambda key: get_relevance(key, tier, "share_structure", stage)

    t = Table(title="Share Structure Analysis", show_lines=True, border_style="bold yellow")
    t.add_column("Indicator", style="bold", min_width=22, no_wrap=True)
    t.add_column("Value", min_width=14)
    t.add_column("Assessment", ratio=1, overflow="fold")

    _add_metric_row(t, "Shares Outstanding", fmt_shares(ss.shares_outstanding),
                    _a_shares_out(ss.shares_outstanding), rel("shares_outstanding"))
    _add_metric_row(t, "Fully Diluted", fmt_shares(ss.fully_diluted_shares),
                    _a_fd_shares(ss.fully_diluted_shares), rel("fully_diluted_shares"))
    _add_metric_row(t, "Float", fmt_shares(ss.float_shares),
                    _a_float(ss.float_shares, ss.shares_outstanding),
                    Relevance.RELEVANT)
    _add_metric_row(t, "Insider Ownership",
                    fmt_pct(ss.insider_ownership_pct) if ss.insider_ownership_pct else "[dim]N/A[/]",
                    _a_insider(ss.insider_ownership_pct), rel("insider_ownership_pct"))
    _add_metric_row(t, "Institutional Ownership",
                    fmt_pct(ss.institutional_ownership_pct) if ss.institutional_ownership_pct else "[dim]N/A[/]",
                    _a_inst(ss.institutional_ownership_pct), rel("institutional_ownership_pct"))
    _add_metric_row(t, "Assessment", ss.share_structure_assessment or "[dim]N/A[/]",
                    _a_ss_assessment(ss.share_structure_assessment), rel("share_structure_assessment"))
    console.print(t)


def _a_float(val, total):
    if _isna(val):
        return "[dim]No float data[/]"
    if not _isna(total) and total > 0:
        pct = val / total
        if pct < 0.40:
            return "[green]Low float — tightly held, high torque[/]"
        if pct < 0.70:
            return "[yellow]Moderate float[/]"
        return "[dim]High float — widely distributed[/]"
    return f"[cyan]{fmt_shares(val)} shares in float[/]"


def _display_energy_quality(report):
    """Energy quality assessment — uses relevance markers via get_relevance with category='energy_quality'."""
    m = report.energy_quality
    if m is None:
        return
    tier, stage = report.profile.tier, report.profile.stage
    rel = lambda key: get_relevance(key, tier, "energy_quality", stage)

    t = Table(title="Energy Quality Assessment", show_lines=True, border_style="bold yellow")
    t.add_column("Indicator", style="bold", min_width=22, no_wrap=True)
    t.add_column("Assessment", ratio=1, overflow="fold")

    # Quality score — special formatting with score color
    r_qs = rel("quality_score")
    if r_qs != Relevance.IRRELEVANT:
        style, prefix = _STYLE[r_qs]
        qs_label = f"{prefix}[{style}]Quality Score[/]" if style else f"{prefix}Quality Score"
        t.add_row(qs_label, fmt_score(m.quality_score))

    # Competitive position — always RELEVANT (no stage override in relevance.py)
    _add_quality_row(t, "Competitive Position", m.competitive_position, Relevance.RELEVANT)

    # Insider alignment
    _add_quality_row(t, "Insider Alignment", m.insider_alignment, rel("insider_alignment"))

    # Financial position
    _add_quality_row(t, "Financial Position", m.financial_position, rel("financial_position"))

    # Dilution risk
    _add_quality_row(t, "Dilution Risk", m.dilution_risk, rel("dilution_risk"))

    # Asset backing
    _add_quality_row(t, "Asset Backing", m.asset_backing, rel("asset_backing"))

    # Revenue predictability
    _add_quality_row(t, "Revenue Status", m.revenue_predictability, rel("revenue_predictability"))

    # Share structure assessment — always shown
    _add_quality_row(t, "Share Structure", m.share_structure_assessment, Relevance.RELEVANT)

    # Management quality — always shown
    _add_quality_row(t, "Management Quality", m.management_quality, Relevance.RELEVANT)

    console.print(t)


def _add_quality_row(table, label, value, relevance):
    """Add a row to the energy quality table with relevance-based styling."""
    if relevance == Relevance.IRRELEVANT:
        return
    style, prefix = _STYLE[relevance]
    sl = f"{prefix}[{style}]{label}[/]" if style else f"{prefix}{label}"
    display_val = value or "[dim]N/A[/]"
    if style and value:
        display_val = f"[{style}]{value}[/]"
    table.add_row(sl, display_val)


def _display_intrinsic_value(report):
    """Intrinsic value estimates with complete margin-of-safety display."""
    iv = report.intrinsic_value
    if iv is None:
        return

    t = Table(title="Intrinsic Value Estimates", show_lines=True, border_style="bold green")
    t.add_column("Method", style="bold", min_width=28, no_wrap=True)
    t.add_column("Value", justify="right", min_width=14, no_wrap=True)
    t.add_column("Margin of Safety", ratio=1, overflow="fold")

    # Current price row
    t.add_row(
        "Current Price",
        f"${iv.current_price:.2f}" if iv.current_price else "[dim]N/A[/]",
        "",
    )

    def _m(name):
        if iv.primary_method and name in iv.primary_method:
            return "[bold green](primary)[/] "
        if iv.secondary_method and name in iv.secondary_method:
            return "[cyan](secondary)[/] "
        return "[dim](reference)[/] "

    # DCF
    if iv.dcf_value:
        t.add_row(
            _m("DCF") + "DCF (10Y)",
            f"${iv.dcf_value:.2f}",
            _mos_color(iv.margin_of_safety_dcf),
        )

    # Graham Number
    if iv.graham_number:
        t.add_row(
            _m("Graham") + "Graham Number",
            f"${iv.graham_number:.2f}",
            _mos_color(iv.margin_of_safety_graham),
        )

    # NCAV Net-Net
    if iv.ncav_value is not None:
        t.add_row(
            _m("NCAV") + "NCAV (Net-Net)",
            f"${iv.ncav_value:.4f}" if iv.ncav_value > 0 else "[dim]Negative[/]",
            _mos_color(iv.margin_of_safety_ncav),
        )

    # Asset-based / Tangible Book
    if iv.asset_based_value:
        t.add_row(
            _m("Asset") + "Tangible Book / Share",
            f"${iv.asset_based_value:.4f}",
            _mos_color(iv.margin_of_safety_asset),
        )

    # NAV per Share (from technical studies)
    if iv.nav_per_share:
        t.add_row(
            _m("NAV") + "NAV / Share (Study)",
            f"${iv.nav_per_share:.2f}",
            _mos_color(iv.margin_of_safety_nav),
        )

    # Summary guidance on margin of safety
    if iv.current_price and any([
        iv.margin_of_safety_dcf, iv.margin_of_safety_graham,
        iv.margin_of_safety_ncav, iv.margin_of_safety_asset,
        iv.margin_of_safety_nav,
    ]):
        mos_values = [
            v for v in [
                iv.margin_of_safety_dcf, iv.margin_of_safety_graham,
                iv.margin_of_safety_ncav, iv.margin_of_safety_asset,
                iv.margin_of_safety_nav,
            ]
            if v is not None
        ]
        if mos_values:
            avg_mos = sum(mos_values) / len(mos_values)
            t.add_row(
                "[bold]Average MoS[/]",
                "",
                _mos_color(avg_mos),
            )

    console.print(t)


def _display_conclusion(report):
    """Final assessment with verdict, scores, strengths/risks, and screening checklist."""
    from lynx_energy.core.conclusion import generate_conclusion
    c = generate_conclusion(report)

    vc = {
        "Strong Buy": "bold green",
        "Buy": "green",
        "Hold": "yellow",
        "Caution": "#ff8800",
        "Avoid": "bold red",
    }.get(c.verdict, "white")

    console.print(Panel(
        f"[{vc}]{c.verdict}[/]  --  Score: {fmt_score(c.overall_score)}\n\n"
        f"{c.summary}\n\n"
        f"[dim]{c.stage_note}[/]\n"
        f"[dim]{c.tier_note}[/]",
        title="[bold]Assessment Conclusion[/]",
        border_style=vc,
    ))

    # Category scores table
    t = Table(title="Category Scores", show_lines=True, border_style="cyan")
    t.add_column("Category", style="bold", min_width=16, no_wrap=True)
    t.add_column("Score", justify="right", min_width=10, no_wrap=True)
    t.add_column("Summary", ratio=1, overflow="fold")
    for cat in ("valuation", "profitability", "solvency", "growth", "energy_quality"):
        t.add_row(
            cat.replace("_", " ").title(),
            fmt_score(c.category_scores.get(cat, 0)),
            c.category_summaries.get(cat, ""),
        )
    console.print(t)

    # Strengths and Risks side-by-side
    if c.strengths or c.risks:
        sr = Table(show_header=True, border_style="green")
        sr.add_column("Strengths", style="green", ratio=1, overflow="fold")
        sr.add_column("Risks", style="red", ratio=1, overflow="fold")
        for i in range(max(len(c.strengths), len(c.risks))):
            sr.add_row(
                c.strengths[i] if i < len(c.strengths) else "",
                c.risks[i] if i < len(c.risks) else "",
            )
        console.print(sr)

    # Screening checklist
    _display_screening(c)


def _display_screening(c):
    """Screening checklist with PASS/FAIL/N/A color coding."""
    if not c.screening_checklist:
        return

    labels = {
        "cash_runway_18m": "Cash Runway >18 months",
        "low_dilution": "Low Dilution (<5%/yr)",
        "insider_ownership": "Insider Ownership >10%",
        "tight_share_structure": "Tight Share Structure (<200M)",
        "no_excessive_debt": "No Excessive Debt",
        "positive_working_capital": "Positive Working Capital",
        "management_track_record": "Management Track Record",
        "tier_1_2_jurisdiction": "Tier 1/2 Jurisdiction",
        "cash_backing": "Cash Backing >30%",
        "has_revenue": "Has Revenue (Producers)",
        "capital_discipline": "Capital Discipline (Capex <80% OCF)",
        "dividend_covered": "Dividend Covered by FCF",
    }

    t = Table(title="Energy Screening Checklist", border_style="cyan")
    t.add_column("Criterion", style="bold", min_width=30, no_wrap=True)
    t.add_column("Result", justify="center", min_width=8, no_wrap=True)

    passed = 0
    total = 0
    for key, val in c.screening_checklist.items():
        label = labels.get(key, key.replace("_", " ").title())
        if val is True:
            t.add_row(label, "[bold green]PASS[/]")
            passed += 1
            total += 1
        elif val is False:
            t.add_row(label, "[bold red]FAIL[/]")
            total += 1
        else:
            t.add_row(label, "[dim]N/A[/]")
    console.print(t)

    if total > 0:
        ratio_pct = passed / total * 100
        color = "green" if ratio_pct >= 80 else "yellow" if ratio_pct >= 50 else "red"
        console.print(
            f"[{color}]  Screening: {passed}/{total} criteria passed ({ratio_pct:.0f}%). "
            f"Target: 8+/10 for high-quality candidates.[/]"
        )


# ---------------------------------------------------------------------------
# Supporting sections (financials, filings, news)
# ---------------------------------------------------------------------------

def _display_market_intelligence(report):
    """Market intelligence — insider activity, analyst consensus, short interest, technicals."""
    mi = report.market_intelligence
    if mi is None:
        return

    # --- Commodity Market Context ---
    if mi.commodity_name or mi.sector_etf_name:
        t = Table(title="Commodity & Sector Context", show_lines=True, border_style="cyan")
        t.add_column("Indicator", style="bold", min_width=22, no_wrap=True)
        t.add_column("Value", min_width=14, no_wrap=True)
        t.add_column("Context", ratio=1, overflow="fold")
        if mi.commodity_name and mi.commodity_price:
            t.add_row("  Commodity", mi.commodity_name, "")
            t.add_row("  Spot Price", f"${mi.commodity_price:,.2f}", "")
            if mi.commodity_52w_high and mi.commodity_52w_low:
                t.add_row("  52W Range", f"${mi.commodity_52w_low:,.2f} - ${mi.commodity_52w_high:,.2f}", "")
            if mi.commodity_52w_position is not None:
                pos = mi.commodity_52w_position
                bar = _range_bar(pos)
                t.add_row("  Price Position", f"{pos*100:.0f}%", bar)
        if mi.sector_etf_name:
            perf_str = f"{mi.sector_etf_3m_perf*100:+.1f}% (3 months)" if mi.sector_etf_3m_perf is not None else ""
            t.add_row("  Sector ETF", f"{mi.sector_etf_name} ({mi.sector_etf_ticker})",
                      f"${mi.sector_etf_price:,.2f}  {perf_str}" if mi.sector_etf_price else "")
        if mi.peer_etf_name:
            perf_str = f"{mi.peer_etf_3m_perf*100:+.1f}% (3 months)" if mi.peer_etf_3m_perf is not None else ""
            t.add_row("  Peer ETF", f"{mi.peer_etf_name} ({mi.peer_etf_ticker})",
                      f"${mi.peer_etf_price:,.2f}  {perf_str}" if mi.peer_etf_price else "")
        console.print(t)

    # --- Analyst Consensus & Price Targets ---
    if mi.analyst_count and mi.analyst_count > 0:
        t = Table(title="Analyst Consensus & Price Targets", show_lines=True, border_style="blue")
        t.add_column("Indicator", style="bold", min_width=22, no_wrap=True)
        t.add_column("Value", min_width=14, no_wrap=True)
        t.add_column("Assessment", ratio=1, overflow="fold")

        rec_display = (mi.recommendation or "N/A").replace("_", " ").title()
        t.add_row("  Recommendation", rec_display, _a_recommendation(mi.recommendation))
        t.add_row("  Analyst Count", str(mi.analyst_count), _a_analyst_count(mi.analyst_count))
        t.add_row("  Target High", f"${mi.target_high:.2f}" if mi.target_high else "[dim]N/A[/]", "")
        t.add_row("  Target Mean", f"${mi.target_mean:.2f}" if mi.target_mean else "[dim]N/A[/]",
                   _a_target_upside(mi.target_upside_pct))
        t.add_row("  Target Low", f"${mi.target_low:.2f}" if mi.target_low else "[dim]N/A[/]", "")
        if mi.target_upside_pct is not None:
            t.add_row("  Upside to Target", fmt_pct(mi.target_upside_pct), _a_target_upside(mi.target_upside_pct))
        console.print(t)

    # --- Short Interest ---
    if mi.shares_short is not None:
        t = Table(title="Short Interest", show_lines=True, border_style="red")
        t.add_column("Indicator", style="bold", min_width=22, no_wrap=True)
        t.add_column("Value", min_width=14, no_wrap=True)
        t.add_column("Assessment", ratio=1, overflow="fold")
        t.add_row("  Shares Short", fmt_shares(mi.shares_short), "")
        t.add_row("  Short % of Float", fmt_pct(mi.short_pct_of_float) if mi.short_pct_of_float else "[dim]N/A[/]",
                   _a_short_pct(mi.short_pct_of_float))
        t.add_row("  Days to Cover", f"{mi.short_ratio_days:.1f}" if mi.short_ratio_days else "[dim]N/A[/]",
                   _a_days_to_cover(mi.short_ratio_days))
        if mi.short_squeeze_risk:
            t.add_row("  Squeeze Risk", mi.short_squeeze_risk, "")
        console.print(t)

    # --- Price Technicals ---
    t = Table(title="Price Technicals & Momentum", show_lines=True, border_style="magenta")
    t.add_column("Indicator", style="bold", min_width=22, no_wrap=True)
    t.add_column("Value", min_width=14, no_wrap=True)
    t.add_column("Assessment", ratio=1, overflow="fold")

    if mi.price_current:
        t.add_row("  Current Price", f"${mi.price_current:.2f}", "")
    if mi.price_52w_high:
        t.add_row("  52-Week High", f"${mi.price_52w_high:.2f}", f"{mi.pct_from_52w_high*100:.1f}% from high" if mi.pct_from_52w_high else "")
    if mi.price_52w_low:
        t.add_row("  52-Week Low", f"${mi.price_52w_low:.2f}", f"{mi.pct_from_52w_low*100:+.1f}% from low" if mi.pct_from_52w_low else "")
    if mi.price_52w_range_position is not None:
        pos = mi.price_52w_range_position
        bar = _range_bar(pos)
        t.add_row("  52W Range Position", f"{pos*100:.0f}%", bar)
    if mi.sma_50:
        above = "[green]Above[/]" if mi.above_sma_50 else "[red]Below[/]"
        t.add_row("  50-Day SMA", f"${mi.sma_50:.2f}", above)
    if mi.sma_200:
        above = "[green]Above[/]" if mi.above_sma_200 else "[red]Below[/]"
        t.add_row("  200-Day SMA", f"${mi.sma_200:.2f}", above)
    if mi.golden_cross is not None:
        signal = "[green]Golden Cross (50d > 200d) — bullish[/]" if mi.golden_cross else "[red]Death Cross (50d < 200d) — bearish[/]"
        t.add_row("  MA Cross Signal", "", signal)
    if mi.beta:
        t.add_row("  Beta", f"{mi.beta:.2f}", _a_beta(mi.beta))
    if mi.volume_trend:
        t.add_row("  Volume Trend", mi.volume_trend, "")
    console.print(t)

    # --- Insider Activity ---
    if mi.insider_transactions:
        t = Table(title="Recent Insider Transactions", show_lines=True, border_style="yellow")
        t.add_column("Date", min_width=12, no_wrap=True)
        t.add_column("Insider", min_width=20)
        t.add_column("Position", min_width=16)
        t.add_column("Action", ratio=1, overflow="fold")
        t.add_column("Shares", justify="right", min_width=10, no_wrap=True)
        for tx in mi.insider_transactions[:8]:
            t.add_row(tx.date, tx.insider, tx.position, tx.transaction_type,
                      f"{tx.shares:,.0f}" if tx.shares else "N/A")
        console.print(t)
        if mi.insider_buy_signal:
            signal_color = "green" if "buying" in mi.insider_buy_signal.lower() else "red" if "selling" in mi.insider_buy_signal.lower() else "yellow"
            console.print(f"  [{signal_color}]Insider Signal: {mi.insider_buy_signal}[/]")

    # --- Top Institutional Holders ---
    if mi.top_holders:
        console.print(f"  [dim]Top Holders ({mi.institutions_count or '?'} institutions, {mi.institutions_pct*100:.1f}% held):[/]" if mi.institutions_pct else "  [dim]Top Holders:[/]")
        for holder in mi.top_holders[:5]:
            console.print(f"    [dim]{holder}[/]")

    # --- Projected Dilution ---
    if mi.financing_warning:
        console.print(Panel(
            f"[bold yellow]{mi.financing_warning}[/]",
            title="[bold yellow]Financing & Dilution Projection[/]",
            border_style="yellow",
        ))

    # --- Risk Warnings ---
    if mi.risk_warnings:
        console.print(Panel(
            "\n".join(f"[bold red]{WARN}[/] {w}" for w in mi.risk_warnings),
            title="[bold red]Risk Warnings[/]",
            border_style="red",
        ))

    # --- Energy Disclaimers ---
    if mi.disclaimers:
        console.print(Panel(
            "\n".join(f"[dim]{d}[/]" for d in mi.disclaimers),
            title="[dim]Energy Investment Disclaimers[/]",
            border_style="dim",
        ))


def _display_financials(report):
    if not report.financials:
        return
    t = Table(title="Financial Statements Summary (Annual)", show_lines=True, border_style="cyan")
    t.add_column("Period", style="bold", no_wrap=True)
    for lbl in ["Revenue", "Gross Profit", "Op. Income", "Net Income", "FCF", "Total Equity", "Total Debt"]:
        t.add_column(lbl, justify="right", min_width=11, no_wrap=True)
    for s in report.financials[:5]:
        t.add_row(
            s.period,
            fmt_money(s.revenue),
            fmt_money(s.gross_profit),
            fmt_money(s.operating_income),
            fmt_money(s.net_income),
            fmt_money(s.free_cash_flow),
            fmt_money(s.total_equity),
            fmt_money(s.total_debt),
        )
    console.print(t)


def _display_filings(report):
    if not report.filings:
        return
    t = Table(
        title=f"SEC/SEDAR Filings (top {min(len(report.filings), 15)})",
        border_style="yellow",
    )
    t.add_column("Type", style="bold", no_wrap=True)
    t.add_column("Filed", no_wrap=True)
    t.add_column("Period", no_wrap=True)
    t.add_column("Downloaded", justify="center", no_wrap=True)
    for f in report.filings[:15]:
        t.add_row(
            f.form_type,
            f.filing_date,
            f.period,
            "[green]Yes[/]" if f.local_path else "[dim]No[/]",
        )
    console.print(t)


def _display_news(report):
    if not report.news:
        return
    t = Table(
        title=f"Recent News ({len(report.news)} articles)",
        border_style="magenta",
    )
    t.add_column("#", style="dim", width=3, no_wrap=True)
    t.add_column("Title", ratio=3, overflow="fold")
    t.add_column("Source", ratio=1, no_wrap=True)
    t.add_column("Date", ratio=1, no_wrap=True)
    for i, n in enumerate(report.news[:15], 1):
        t.add_row(str(i), n.title or "", n.source or "", n.published or "")
    console.print(t)
