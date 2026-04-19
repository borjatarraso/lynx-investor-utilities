"""Energy-focused report synthesis engine."""

from __future__ import annotations

import math

from lynx_energy.models import AnalysisConclusion, AnalysisReport, CompanyStage, CompanyTier, JurisdictionTier


def _safe(val, default: float = 0.0) -> float:
    if val is None or isinstance(val, bool):
        return default
    try:
        f = float(val)
        return default if (math.isnan(f) or math.isinf(f)) else f
    except (TypeError, ValueError):
        return default


_WEIGHTS = {
    (CompanyStage.PRODUCER, CompanyTier.MEGA): (0.25, 0.25, 0.15, 0.15, 0.20),
    (CompanyStage.PRODUCER, CompanyTier.LARGE): (0.25, 0.25, 0.15, 0.15, 0.20),
    (CompanyStage.PRODUCER, CompanyTier.MID): (0.20, 0.20, 0.20, 0.20, 0.20),
    (CompanyStage.PRODUCER, CompanyTier.SMALL): (0.15, 0.15, 0.25, 0.20, 0.25),
    (CompanyStage.PRODUCER, CompanyTier.MICRO): (0.15, 0.15, 0.25, 0.20, 0.25),
    (CompanyStage.PRODUCER, CompanyTier.NANO): (0.10, 0.10, 0.30, 0.20, 0.30),
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
    c.screening_checklist = _energy_screening(report)
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
    pe = _safe(v.pe_trailing, None)
    if pe is not None:
        if pe < 0: pass
        elif pe < 10: score += 25
        elif pe < 15: score += 15
        elif pe < 20: score += 5
        elif pe < 30: score -= 5
        else: score -= 15
    pb = _safe(v.pb_ratio, None)
    if pb is not None:
        if pb < 1: score += 20
        elif pb < 1.5: score += 10
        elif pb >= 3: score -= 10
    ctm = _safe(v.cash_to_market_cap, None)
    if ctm is not None:
        if ctm > 0.50: score += 15
        elif ctm > 0.30: score += 8
        elif ctm > 0.15: score += 3
    ev = _safe(v.ev_ebitda, None)
    if ev is not None:
        if ev < 5: score += 15
        elif ev < 8: score += 10
        elif ev >= 12: score -= 10
    return max(0, min(100, score))


def _score_profitability(r: AnalysisReport) -> float:
    if r.profile.stage in (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER):
        return 50.0
    p = r.profitability
    if p is None:
        return 50.0
    score = 50.0
    roe = _safe(p.roe, None)
    if roe is not None:
        if roe > 0.20: score += 15
        elif roe > 0.10: score += 5
        elif roe < 0: score -= 15
    gm = _safe(p.gross_margin, None)
    if gm is not None:
        if gm > 0.50: score += 10
        elif gm > 0.30: score += 5
        elif gm < 0.10: score -= 10
    nm = _safe(p.net_margin, None)
    if nm is not None:
        if nm > 0.15: score += 10
        elif nm > 0.05: score += 5
        elif nm < 0: score -= 15
    return max(0, min(100, score))


def _score_solvency(r: AnalysisReport) -> float:
    s = r.solvency
    if s is None:
        return 50.0
    score = 50.0
    stage = r.profile.stage
    de = _safe(s.debt_to_equity, None)
    if de is not None:
        if stage in (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER):
            if de < 0: score += 15
            elif de < 0.1: score += 10
            elif de > 0.5: score -= 20
        else:
            if de < 0: score += 15
            elif de < 0.5: score += 10
            elif de > 2: score -= 15
    cr = _safe(s.current_ratio, None)
    if cr is not None:
        if cr > 3: score += 12
        elif cr > 2: score += 8
        elif cr > 1.5: score += 5
        elif cr < 1: score -= 15
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
    return max(0, min(100, score))


def _score_growth(r: AnalysisReport) -> float:
    g = r.growth
    if g is None:
        return 50.0
    score = 50.0
    stage = r.profile.stage
    if stage in (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER, CompanyStage.DEVELOPER):
        dil = _safe(g.shares_growth_yoy, None)
        if dil is not None:
            if dil < 0.01: score += 15
            elif dil < 0.05: score += 5
            elif dil > 0.20: score -= 25
            elif dil > 0.10: score -= 15
        bv = _safe(g.book_value_growth_yoy, None)
        if bv is not None:
            if bv > 0.10: score += 10
            elif bv > 0: score += 5
            elif bv < -0.10: score -= 10
        return max(0, min(100, score))
    rg = _safe(g.revenue_growth_yoy, None)
    if rg is not None:
        if rg > 0.20: score += 15
        elif rg > 0.05: score += 5
        elif rg < -0.10: score -= 15
    dil = _safe(g.shares_growth_yoy, None)
    if dil is not None:
        if dil < -0.02: score += 5
        elif dil > 0.10: score -= 10
    return max(0, min(100, score))


def _energy_screening(r: AnalysisReport) -> dict:
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
    checks["low_dilution"] = dil < 0.05 if dil is not None else None

    insider = _safe(ss.insider_ownership_pct, None) if ss else None
    checks["insider_ownership"] = insider > 0.10 if insider is not None else None

    fd = _safe(ss.fully_diluted_shares, None) if ss else None
    checks["tight_share_structure"] = fd < 200_000_000 if fd is not None else None

    de = _safe(s.debt_to_equity, None) if s else None
    if de is not None:
        checks["no_excessive_debt"] = de < 0.3 if stage in (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER) else de < 1.5
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

    return checks


def _build_summaries(r: AnalysisReport) -> dict[str, str]:
    summaries: dict[str, str] = {}
    stage = r.profile.stage
    if stage in (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER):
        ctm = _safe(r.valuation.cash_to_market_cap, None) if r.valuation else None
        summaries["valuation"] = f"Cash backing: {ctm*100:.0f}% of market cap" if ctm else "Limited valuation data for explorer"
    else:
        pe = _safe(r.valuation.pe_trailing, None) if r.valuation else None
        summaries["valuation"] = f"P/E of {pe:.1f}" if pe else "Limited valuation data"
    if stage in (CompanyStage.GRASSROOTS, CompanyStage.EXPLORER):
        summaries["profitability"] = "Pre-revenue — not applicable"
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
        if _safe(r.solvency.debt_to_equity, None) is not None and r.solvency.debt_to_equity < 0.2:
            strengths.append("Conservative balance sheet")
    if r.valuation:
        ctm = _safe(r.valuation.cash_to_market_cap, None)
        if ctm and ctm > 0.40:
            strengths.append(f"Strong cash backing ({ctm*100:.0f}% of market cap)")
        pb = _safe(r.valuation.pb_ratio, None)
        if pb is not None and pb < 1:
            strengths.append(f"Below book value (P/B {pb:.2f})")
    if r.share_structure:
        if r.share_structure.share_structure_assessment and "Tight" in r.share_structure.share_structure_assessment:
            strengths.append("Tight share structure")
        insider = _safe(r.share_structure.insider_ownership_pct, None)
        if insider and insider > 0.15:
            strengths.append(f"Strong insider ownership ({insider*100:.0f}%)")
    if r.growth:
        dil = _safe(r.growth.shares_growth_yoy, None)
        if dil is not None and dil < 0.02:
            strengths.append("Minimal share dilution")
    if r.profile.jurisdiction_tier == JurisdictionTier.TIER_1:
        strengths.append("Tier 1 energy jurisdiction")
    return strengths[:6]


def _find_risks(r: AnalysisReport) -> list[str]:
    risks = []
    if r.solvency:
        runway = _safe(r.solvency.cash_runway_years, None)
        if runway is not None and runway < 1.5:
            risks.append(f"Limited cash runway ({runway:.1f} years)")
        bpct = _safe(r.solvency.burn_as_pct_of_market_cap, None)
        if bpct and bpct > 0.08:
            risks.append(f"High burn rate ({bpct*100:.0f}% of market cap/yr)")
    if r.growth:
        dil = _safe(r.growth.shares_growth_yoy, None)
        if dil is not None and dil > 0.10:
            risks.append(f"Heavy share dilution ({dil*100:.1f}%/yr)")
    if r.share_structure and r.share_structure.share_structure_assessment and "Bloated" in r.share_structure.share_structure_assessment:
        risks.append("Bloated share structure (>500M shares)")
    if r.profile.jurisdiction_tier == JurisdictionTier.TIER_3:
        risks.append("Tier 3 jurisdiction — high geopolitical risk")
    if r.profile.stage == CompanyStage.GRASSROOTS:
        risks.append("Early exploration stage — binary outcome risk")
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
        CompanyTier.MEGA: "Full traditional analysis. DCF and ROIC primary.",
        CompanyTier.LARGE: "Full traditional analysis. All metrics reliable.",
        CompanyTier.MID: "Blended analysis. Growth weighted more heavily.",
        CompanyTier.SMALL: "Balance sheet critical. Cash runway and dilution are key.",
        CompanyTier.MICRO: "Survival metrics dominate. Cash runway, dilution, share structure critical.",
        CompanyTier.NANO: "Speculative. Asset-based valuation only. High risk.",
    }.get(tier, "")


def _stage_note(stage: CompanyStage) -> str:
    return {
        CompanyStage.PRODUCER: "Producer: traditional metrics + netback/production costs. EV/EBITDA and FCF yield primary.",
        CompanyStage.DEVELOPER: "Developer: P/NAV from field development economics. Cash runway critical. Cost overruns (20-40%) common.",
        CompanyStage.EXPLORER: "Explorer: EV/BOE reserves and P/NAV. Cash runway, dilution, acreage quality are key. Pre-revenue.",
        CompanyStage.GRASSROOTS: "Early Exploration: call option on discovery. Cash backing, management, land position. Binary risk.",
        CompanyStage.ROYALTY: "Royalty/Streaming: premium model. DCF primary. Diversified, no operating risk, high margins.",
    }.get(stage, "")
