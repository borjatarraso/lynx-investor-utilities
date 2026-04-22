"""Utilities-focused report synthesis engine."""

from __future__ import annotations

import math

from lynx_utilities.models import AnalysisConclusion, AnalysisReport, CompanyStage, CompanyTier, JurisdictionTier


def _safe(val, default: float = 0.0) -> float:
    if val is None or isinstance(val, bool):
        return default
    try:
        f = float(val)
        return default if (math.isnan(f) or math.isinf(f)) else f
    except (TypeError, ValueError):
        return default


# Category weight order: valuation, profitability, solvency, growth, utility-quality.
# Operating utilities have balanced weights with heavier emphasis on profitability
# and growth (the rate-base-growth story). Pre-operational developers lean
# heavily on solvency and quality because there is no meaningful earnings yet.
_WEIGHTS = {
    (CompanyStage.PRODUCER, CompanyTier.MEGA): (0.20, 0.25, 0.20, 0.15, 0.20),
    (CompanyStage.PRODUCER, CompanyTier.LARGE): (0.20, 0.25, 0.20, 0.15, 0.20),
    (CompanyStage.PRODUCER, CompanyTier.MID): (0.20, 0.20, 0.25, 0.15, 0.20),
    (CompanyStage.PRODUCER, CompanyTier.SMALL): (0.15, 0.15, 0.30, 0.15, 0.25),
    (CompanyStage.PRODUCER, CompanyTier.MICRO): (0.15, 0.15, 0.30, 0.15, 0.25),
    (CompanyStage.PRODUCER, CompanyTier.NANO): (0.10, 0.10, 0.35, 0.15, 0.30),
    (CompanyStage.DEVELOPER, CompanyTier.SMALL): (0.10, 0.10, 0.35, 0.15, 0.30),
    (CompanyStage.DEVELOPER, CompanyTier.MICRO): (0.10, 0.10, 0.35, 0.15, 0.30),
    (CompanyStage.DEVELOPER, CompanyTier.NANO): (0.05, 0.05, 0.40, 0.15, 0.35),
    (CompanyStage.EXPLORER, CompanyTier.SMALL): (0.10, 0.05, 0.35, 0.15, 0.35),
    (CompanyStage.EXPLORER, CompanyTier.MICRO): (0.10, 0.05, 0.35, 0.15, 0.35),
    (CompanyStage.EXPLORER, CompanyTier.NANO): (0.05, 0.05, 0.40, 0.15, 0.35),
    (CompanyStage.GRASSROOTS, CompanyTier.MICRO): (0.05, 0.05, 0.40, 0.15, 0.35),
    (CompanyStage.GRASSROOTS, CompanyTier.NANO): (0.05, 0.05, 0.40, 0.15, 0.35),
    (CompanyStage.ROYALTY, CompanyTier.SMALL): (0.25, 0.20, 0.15, 0.20, 0.20),
    (CompanyStage.ROYALTY, CompanyTier.MID): (0.25, 0.25, 0.15, 0.15, 0.20),
    (CompanyStage.ROYALTY, CompanyTier.LARGE): (0.25, 0.25, 0.15, 0.15, 0.20),
}
_DEFAULT_WEIGHTS = (0.15, 0.10, 0.30, 0.15, 0.30)


def generate_conclusion(report: AnalysisReport) -> AnalysisConclusion:
    c = AnalysisConclusion()
    tier, stage = report.profile.tier, report.profile.stage

    val_score = _score_valuation(report)
    prof_score = _score_profitability(report)
    solv_score = _score_solvency(report)
    grow_score = _score_growth(report)
    quality_score = _safe(report.energy_quality.quality_score) if report.energy_quality else 0

    c.category_scores = {"valuation": round(val_score, 1), "profitability": round(prof_score, 1),
                         "solvency": round(solv_score, 1), "growth": round(grow_score, 1),
                         "energy_quality": round(quality_score, 1)}

    w = _WEIGHTS.get((stage, tier), _DEFAULT_WEIGHTS)
    c.overall_score = round(val_score * w[0] + prof_score * w[1] + solv_score * w[2] + grow_score * w[3] + quality_score * w[4], 1)
    c.verdict = _verdict(c.overall_score)
    c.category_summaries = _build_summaries(report)
    c.strengths = _find_strengths(report)
    c.risks = _find_risks(report)
    c.summary = _build_narrative(report, c)
    c.tier_note = _tier_note(tier)
    c.stage_note = _stage_note(stage)
    c.screening_checklist = _utilities_screening(report)
    return c


def _verdict(score: float) -> str:
    if score >= 75: return "Strong Buy"
    if score >= 60: return "Buy"
    if score >= 45: return "Hold"
    if score >= 30: return "Caution"
    return "Avoid"


def _score_valuation(r: AnalysisReport) -> float:
    v = r.valuation
    if v is None:
        return 50.0
    score = 50.0
    # Utilities have structurally higher P/E (14-20x normal). Calibrate thresholds.
    pe = _safe(v.pe_trailing, None)
    if pe is not None:
        if pe < 0: pass
        elif pe < 12: score += 20
        elif pe < 16: score += 10
        elif pe < 20: score += 2
        elif pe < 25: score -= 5
        else: score -= 12
    # P/B 1.7-2.2 is normal for regulated utilities (rate base premium).
    pb = _safe(v.pb_ratio, None)
    if pb is not None:
        if pb < 1.2: score += 15
        elif pb < 1.8: score += 8
        elif pb >= 3.0: score -= 8
    ctm = _safe(v.cash_to_market_cap, None)
    if ctm is not None:
        # Large cash backing is uncommon at operating utilities; only reward
        # for pre-operational developers.
        if r.profile.stage in (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER, CompanyStage.DEVELOPER):
            if ctm > 0.50: score += 15
            elif ctm > 0.30: score += 8
            elif ctm > 0.15: score += 3
    # EV/EBITDA benchmarks: regulated 9-12, IPPs 6-9, water 13-17.
    ev = _safe(v.ev_ebitda, None)
    if ev is not None:
        if ev < 7: score += 15
        elif ev < 10: score += 8
        elif ev >= 14: score -= 10
    # Dividend yield — meaningful valuation anchor for utilities.
    dy = _safe(v.dividend_yield, None)
    if dy is not None:
        if 0.04 <= dy <= 0.06: score += 8        # sweet spot
        elif 0.03 <= dy < 0.04: score += 3
        elif dy > 0.07: score -= 5               # stressed / cut risk
        elif dy > 0 and dy < 0.02: score -= 3    # unusually low for sector
    # FCF yield: at utilities, a positive FCF yield indicates harvest mode.
    fcf_y = _safe(v.fcf_yield, None)
    if fcf_y is not None:
        if fcf_y > 0.06: score += 6
        elif fcf_y > 0.02: score += 2
    return max(0, min(100, score))


def _score_profitability(r: AnalysisReport) -> float:
    if r.profile.stage in (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER):
        return 50.0
    p = r.profitability
    if p is None:
        return 50.0
    score = 50.0
    # Utility ROE: 8-12% is typical (tied to allowed ROE). Above 13% is exceptional.
    roe = _safe(p.roe, None)
    if roe is not None:
        if roe > 0.13: score += 15
        elif roe > 0.09: score += 8
        elif roe > 0.06: score += 2
        elif roe < 0: score -= 15
        elif roe < 0.05: score -= 5
    # Gross margin is distorted by pass-throughs; small weight.
    gm = _safe(p.gross_margin, None)
    if gm is not None:
        if gm > 0.45: score += 5
        elif gm < 0.15: score -= 5
    # Utility net margins: 8-12% normal.
    nm = _safe(p.net_margin, None)
    if nm is not None:
        if nm > 0.14: score += 10
        elif nm > 0.07: score += 5
        elif nm < 0: score -= 15
    # EBITDA margin is the preferred utility profitability read.
    em = _safe(p.ebitda_margin, None)
    if em is not None:
        if em > 0.35: score += 6
        elif em < 0.20: score -= 5
    # CROCI cross-check
    croci = _safe(p.croci, None)
    if croci is not None:
        if croci > 0.10: score += 6
        elif croci > 0.06: score += 3
        elif croci < 0: score -= 8
    return max(0, min(100, score))


def _score_solvency(r: AnalysisReport) -> float:
    s = r.solvency
    if s is None:
        return 50.0
    score = 50.0
    stage = r.profile.stage
    # Utilities are structurally leveraged. Operating utilities at D/E 1.0-1.5 is normal.
    de = _safe(s.debt_to_equity, None)
    if de is not None:
        if stage in (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER):
            if de == 0: score += 15
            elif de < 0.1: score += 10
            elif de > 0.5: score -= 20
        else:
            # Operating utility: penalize only extreme leverage.
            if de < 0.8: score += 10
            elif de <= 1.5: score += 3
            elif de > 2.5: score -= 15
            elif de > 2.0: score -= 5
    # Utilities often have current ratio <1 (working capital funded via revolver).
    # Only heavily penalize very weak positions for developers.
    cr = _safe(s.current_ratio, None)
    if cr is not None:
        if stage in (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER, CompanyStage.DEVELOPER):
            if cr > 3: score += 12
            elif cr > 2: score += 8
            elif cr > 1.5: score += 4
            elif cr < 1: score -= 15
        else:
            if cr < 0.5: score -= 8
            elif cr > 2: score += 4
    burn = _safe(s.cash_burn_rate, None)
    if burn is not None and burn < 0:
        runway = _safe(s.cash_runway_years, None)
        if runway is not None:
            if runway > 3: score += 5
            elif runway < 1: score -= 25
            elif runway < 1.5: score -= 15
            elif runway < 2: score -= 5
    bpct = _safe(s.burn_as_pct_of_market_cap, None)
    if bpct is not None and bpct > 0.08:
        score -= 10
    # Interest coverage is the practical utility credit metric.
    ic = _safe(s.interest_coverage, None)
    if ic is not None and stage not in (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER):
        if ic > 4: score += 8
        elif ic > 2.5: score += 3
        elif ic < 1.5: score -= 12
    # Debt service coverage
    dsc = _safe(s.debt_service_coverage, None)
    if dsc is not None:
        if dsc > 6: score += 5
        elif dsc < 1.5: score -= 10
    return max(0, min(100, score))


def _score_growth(r: AnalysisReport) -> float:
    g = r.growth
    if g is None:
        return 50.0
    score = 50.0
    stage = r.profile.stage
    if stage in (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER, CompanyStage.DEVELOPER):
        # Pre-operational: dilution is the key growth-stage risk.
        dil = _safe(g.shares_growth_yoy, None)
        if dil is not None:
            if dil < 0.02: score += 15
            elif dil < 0.05: score += 5
            elif dil > 0.15: score -= 25
            elif dil > 0.08: score -= 15
        bv = _safe(g.book_value_growth_yoy, None)
        if bv is not None:
            if bv > 0.10: score += 10
            elif bv > 0: score += 5
            elif bv < -0.10: score -= 10
        return max(0, min(100, score))
    # Operating utility: revenue growth is distorted by fuel pass-throughs.
    # Earnings growth (EPS) is the better read.
    eg = _safe(g.earnings_growth_yoy, None)
    if eg is not None:
        if eg > 0.08: score += 12
        elif eg > 0.04: score += 5
        elif eg < -0.10: score -= 15
    rg = _safe(g.revenue_growth_yoy, None)
    if rg is not None:
        if rg > 0.08: score += 4
        elif rg < -0.10: score -= 5
    # Dilution: utilities routinely issue equity. 2-5% is normal; above 6% is dilutive.
    dil = _safe(g.shares_growth_yoy, None)
    if dil is not None:
        if dil < 0.02: score += 5
        elif dil > 0.07: score -= 10
        elif dil > 0.05: score -= 4
    # Dividend coverage check: central utility discipline metric.
    div_cov = _safe(g.dividend_coverage, None)
    if div_cov is not None:
        if div_cov > 1.5: score += 6
        elif div_cov < 0.8: score -= 10
    return max(0, min(100, score))


def _utilities_screening(r: AnalysisReport) -> dict:
    """Utility-focused screening checklist — keys retained for schema parity."""
    checks = {}
    s, g, ss = r.solvency, r.growth, r.share_structure
    stage = r.profile.stage

    runway = _safe(s.cash_runway_years, None) if s else None
    if runway is not None:
        checks["cash_runway_18m"] = runway > 1.5
    elif s and _safe(s.cash_burn_rate, None) is not None and s.cash_burn_rate >= 0:
        checks["cash_runway_18m"] = True
    else:
        checks["cash_runway_18m"] = None

    dil = _safe(g.shares_growth_yoy, None) if g else None
    # For operating utilities 5% is a fair cutoff; stricter 5% for developers.
    checks["low_dilution"] = dil < 0.05 if dil is not None else None

    insider = _safe(ss.insider_ownership_pct, None) if ss else None
    # Utility insider ownership is typically low; reward anything above 2%.
    if insider is not None:
        checks["insider_ownership"] = insider > 0.02 if stage == CompanyStage.PRODUCER else insider > 0.05
    else:
        checks["insider_ownership"] = None

    fd = _safe(ss.fully_diluted_shares, None) if ss else None
    # Utility share counts are larger than juniors; loosen to 2B.
    checks["tight_share_structure"] = fd < 2_000_000_000 if fd is not None else None

    de = _safe(s.debt_to_equity, None) if s else None
    if de is not None:
        if stage in (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER):
            checks["no_excessive_debt"] = de < 0.3
        else:
            checks["no_excessive_debt"] = de < 2.5    # utility-appropriate
    else:
        checks["no_excessive_debt"] = None

    wc = _safe(s.working_capital, None) if s else None
    checks["positive_working_capital"] = wc > 0 if wc is not None else None
    checks["management_track_record"] = None

    jt = r.profile.jurisdiction_tier
    checks["tier_1_2_jurisdiction"] = jt in (JurisdictionTier.TIER_1, JurisdictionTier.TIER_2) if jt != JurisdictionTier.UNKNOWN else None

    if stage in (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER):
        ctm = _safe(r.valuation.cash_to_market_cap, None) if r.valuation else None
        checks["cash_backing"] = ctm > 0.30 if ctm is not None else None
    else:
        checks["cash_backing"] = None

    if stage == CompanyStage.PRODUCER:
        checks["has_revenue"] = any(fs.revenue and fs.revenue > 0 for fs in r.financials)
    else:
        checks["has_revenue"] = None

    # Utility-specific capital discipline and dividend checks
    if stage == CompanyStage.PRODUCER and g:
        # Utilities routinely reinvest >=100% of OCF; discipline means <150%.
        capex_ocf = _safe(g.capex_to_ocf, None)
        checks["capital_discipline"] = capex_ocf < 1.5 if capex_ocf is not None else None
        div_cov = _safe(g.dividend_coverage, None)
        checks["dividend_covered"] = div_cov > 1.0 if div_cov is not None else None
    else:
        checks["capital_discipline"] = None
        checks["dividend_covered"] = None

    return checks


def _build_summaries(r: AnalysisReport) -> dict[str, str]:
    summaries: dict[str, str] = {}
    stage = r.profile.stage
    if stage in (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER):
        ctm = _safe(r.valuation.cash_to_market_cap, None) if r.valuation else None
        summaries["valuation"] = f"Cash backing: {ctm*100:.0f}% of market cap" if ctm else "Limited valuation data for pre-operational developer"
    else:
        pe = _safe(r.valuation.pe_trailing, None) if r.valuation else None
        summaries["valuation"] = f"P/E of {pe:.1f}" if pe else "Limited valuation data"
    if stage in (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER):
        summaries["profitability"] = "Pre-operational — no meaningful earnings"
    else:
        nm = _safe(r.profitability.net_margin, None) if r.profitability else None
        summaries["profitability"] = f"Net margin: {nm*100:.1f}%" if nm is not None else "Limited data"
    if r.solvency:
        runway = _safe(r.solvency.cash_runway_years, None)
        if runway is not None:
            summaries["solvency"] = f"Cash runway: {runway:.1f} years"
        elif _safe(r.solvency.cash_burn_rate, None) is not None and r.solvency.cash_burn_rate >= 0:
            summaries["solvency"] = "Cash flow positive"
        else:
            summaries["solvency"] = "Limited solvency data"
    else:
        summaries["solvency"] = "Limited solvency data"
    dil = _safe(r.growth.shares_growth_yoy, None) if r.growth else None
    summaries["growth"] = f"Share dilution: {dil*100:.1f}%/yr" if dil is not None else "Limited growth data"
    summaries["energy_quality"] = (r.energy_quality.competitive_position or "N/A") if r.energy_quality else "N/A"
    return summaries


def _find_strengths(r: AnalysisReport) -> list[str]:
    strengths = []
    if r.solvency:
        runway = _safe(r.solvency.cash_runway_years, None)
        if runway and runway > 3:
            strengths.append(f"Strong cash position ({runway:.1f} years runway)")
        ic = _safe(r.solvency.interest_coverage, None)
        if ic is not None and ic > 4:
            strengths.append(f"Comfortable interest coverage ({ic:.1f}x)")
    if r.valuation:
        dy = _safe(r.valuation.dividend_yield, None)
        if dy is not None and 0.035 <= dy <= 0.055:
            strengths.append(f"Attractive dividend yield ({dy*100:.1f}%)")
        pb = _safe(r.valuation.pb_ratio, None)
        if pb is not None and pb < 1.3:
            strengths.append(f"Trading near book / rate base (P/B {pb:.2f})")
    if r.profitability:
        roe = _safe(r.profitability.roe, None)
        if roe is not None and roe > 0.11:
            strengths.append(f"Solid ROE ({roe*100:.1f}%) — likely at or above allowed")
    if r.growth:
        dc = _safe(r.growth.dividend_coverage, None)
        if dc is not None and dc > 1.5:
            strengths.append(f"Well-covered dividend ({dc:.1f}x FCF coverage)")
        dil = _safe(r.growth.shares_growth_yoy, None)
        if dil is not None and dil < 0.02:
            strengths.append("Minimal share dilution")
    if r.profile.jurisdiction_tier == JurisdictionTier.TIER_1:
        strengths.append("Tier 1 regulatory jurisdiction")
    return strengths[:6]


def _find_risks(r: AnalysisReport) -> list[str]:
    risks = []
    if r.solvency:
        runway = _safe(r.solvency.cash_runway_years, None)
        if runway is not None and runway < 1.5:
            risks.append(f"Limited cash runway ({runway:.1f} years)")
        ic = _safe(r.solvency.interest_coverage, None)
        if ic is not None and ic < 2.0:
            risks.append(f"Thin interest coverage ({ic:.1f}x) — credit-rating risk")
        de = _safe(r.solvency.debt_to_equity, None)
        if de is not None and de > 2.5:
            risks.append(f"Elevated leverage (D/E {de:.2f})")
    if r.growth:
        dil = _safe(r.growth.shares_growth_yoy, None)
        if dil is not None and dil > 0.07:
            risks.append(f"Heavy equity issuance ({dil*100:.1f}%/yr)")
        dc = _safe(r.growth.dividend_coverage, None)
        if dc is not None and dc < 0.8:
            risks.append(f"Dividend not covered by FCF ({dc:.1f}x)")
    if r.profile.jurisdiction_tier == JurisdictionTier.TIER_3:
        risks.append("Tier 3 jurisdiction — challenging regulatory environment")
    if r.profile.stage == CompanyStage.GRASSROOTS:
        risks.append("Early-stage developer — binary pipeline / financing risk")
    return risks[:6]


def _build_narrative(r: AnalysisReport, c: AnalysisConclusion) -> str:
    parts = [f"{r.profile.name} ({r.profile.tier.value}, {r.profile.stage.value}) scores {c.overall_score:.0f}/100 — '{c.verdict}'."]
    if c.strengths:
        parts.append(f"Strengths: {c.strengths[0].lower()}" + (f" and {c.strengths[1].lower()}" if len(c.strengths) > 1 else "") + ".")
    if c.risks:
        parts.append(f"Risks: {c.risks[0].lower()}" + (f" and {c.risks[1].lower()}" if len(c.risks) > 1 else "") + ".")
    return " ".join(parts)


def _tier_note(tier: CompanyTier) -> str:
    return {
        CompanyTier.MEGA: "Full traditional analysis. DDM and P/Rate Base primary.",
        CompanyTier.LARGE: "Full traditional analysis. All metrics reliable.",
        CompanyTier.MID: "Blended analysis. Rate-base-growth and ROE gap weighted more heavily.",
        CompanyTier.SMALL: "Balance sheet critical. Credit metrics, dividend coverage, and rate case exposure are key.",
        CompanyTier.MICRO: "Survival and financing metrics dominate. Equity issuance cadence and leverage are critical.",
        CompanyTier.NANO: "Speculative. Asset-based / pipeline-NPV valuation only. High risk.",
    }.get(tier, "")


def _stage_note(stage: CompanyStage) -> str:
    return {
        CompanyStage.PRODUCER: "Operating utility: rate-base growth + earned-vs-allowed ROE gap. EV/EBITDA, dividend yield & FFO/Debt primary.",
        CompanyStage.DEVELOPER: "Construction phase: P/NAV of contracted pipeline. Cash runway and equity-issuance cadence critical. Cost overruns common.",
        CompanyStage.EXPLORER: "Development stage: pipeline GW and PPA coverage drive value. Dilution risk, permitting timelines, cost of capital are key.",
        CompanyStage.GRASSROOTS: "Early-stage developer: call option on pipeline maturation. Cash backing, management, and interconnection queue position. Binary risk.",
        CompanyStage.ROYALTY: "YieldCo / holding: premium model. DDM / CAFD multiple primary. Contracted cash flows, little operating risk, high payout.",
    }.get(stage, "")
