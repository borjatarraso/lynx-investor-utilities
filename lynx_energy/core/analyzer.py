"""Main analysis orchestrator for energy companies."""

from __future__ import annotations

import dataclasses
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional

from rich.console import Console

from lynx_energy.core.fetcher import fetch_company_profile, fetch_financial_statements, fetch_info
from lynx_energy.core.news import fetch_all_news
from lynx_energy.core.reports import download_top_filings, fetch_sec_filings
from lynx_energy.core.storage import get_cache_age_hours, has_cache, load_cached_report, save_analysis_report
from lynx_energy.core.ticker import resolve_identifier
from lynx_energy.metrics.calculator import (
    calc_efficiency, calc_growth, calc_intrinsic_value, calc_market_intelligence,
    calc_energy_quality, calc_profitability, calc_share_structure, calc_solvency,
    calc_valuation,
)
from lynx_energy.models import (
    AnalysisReport, CompanyProfile, CompanyStage, CompanyTier,
    EfficiencyMetrics, Filing, FinancialStatement, GrowthMetrics,
    InsiderTransaction, IntrinsicValue, MarketIntelligence,
    EnergyQualityIndicators, NewsArticle,
    ProfitabilityMetrics, ShareStructure, SolvencyMetrics, ValuationMetrics,
    classify_commodity, classify_jurisdiction, classify_stage, classify_tier,
)

console = Console(stderr=True)

# Sectors and industries that this tool is designed for
_ALLOWED_SECTORS = {"energy"}
_ALLOWED_INDUSTRIES = {
    "oil & gas e&p", "oil & gas integrated", "oil & gas midstream",
    "oil & gas refining & marketing", "oil & gas equipment & services",
    "thermal coal", "uranium", "solar", "renewable utilities",
    "oil & gas drilling", "oil & gas exploration & production",
    "independent oil & gas", "major integrated oil & gas",
}


class SectorMismatchError(Exception):
    """Raised when a company does not belong to the energy sector."""
    pass


def _validate_sector(profile: CompanyProfile) -> None:
    """Check if the company belongs to the energy sector.

    Raises SectorMismatchError if the company is outside scope.
    """
    sector = (profile.sector or "").lower().strip()
    industry = (profile.industry or "").lower().strip()

    # Allow if sector matches
    if sector in _ALLOWED_SECTORS:
        return

    # Allow if industry matches any known energy industry
    if industry:
        for allowed in _ALLOWED_INDUSTRIES:
            if allowed in industry or industry in allowed:
                return

    # Allow if the description mentions energy-specific terms (not generic ones)
    desc = (profile.description or "").lower()
    energy_specific = [
        r"\bcrude oil\b", r"\bpetroleum\b", r"\bnatural gas\b",
        r"\boil.{0,15}gas\b", r"\boil.{0,10}production\b",
        r"\bgas.{0,10}production\b", r"\boil.{0,10}exploration\b",
        r"\bpipeline\b", r"\brefinery\b", r"\brefining\b",
        r"\bupstream.{0,30}downstream\b", r"\bmidstream\b",
        r"\bdrilling\b", r"\boil.?field\b", r"\bwellhead\b",
        r"\breservoir\b", r"\bbarrels?\s+(of\s+)?oil\b", r"\bboe\b",
        r"\be&p\b", r"\blng\b", r"\bngl\b",
        r"\buranium\b", r"\bnuclear\b",
        r"\bthermal coal\b", r"\bcoal mine\b", r"\bcoal mining\b",
    ]
    if any(re.search(pattern, desc) for pattern in energy_specific):
        return

    raise SectorMismatchError(
        f"{profile.name} ({profile.ticker}) is in the "
        f"'{profile.sector or 'Unknown'}' / '{profile.industry or 'Unknown'}' "
        f"sector, which is outside the scope of this tool.\n\n"
        f"Lynx Energy Analysis is specialized exclusively for:\n"
        f"  - Energy (Oil & Gas, Uranium, Coal, Renewables)\n\n"
        f"For general fundamental analysis, use lynx-fundamental instead."
    )

ProgressCallback = Callable[[str, AnalysisReport], None]


def run_full_analysis(identifier: str, download_reports: bool = True, download_news: bool = True,
                      max_filings: int = 10, verbose: bool = False, refresh: bool = False) -> AnalysisReport:
    return run_progressive_analysis(identifier=identifier, download_reports=download_reports,
        download_news=download_news, max_filings=max_filings, verbose=verbose, refresh=refresh, on_progress=None)


def run_progressive_analysis(
    identifier: str, download_reports: bool = True, download_news: bool = True,
    max_filings: int = 10, verbose: bool = False, refresh: bool = False,
    on_progress: Optional[ProgressCallback] = None,
) -> AnalysisReport:
    def _notify(stage: str, report: AnalysisReport) -> None:
        if on_progress is not None:
            on_progress(stage, report)

    console.print(f"[bold cyan]Resolving identifier:[/] {identifier}")
    ticker, isin = resolve_identifier(identifier)
    console.print(f"[green]Ticker:[/] {ticker}" + (f"  [dim]ISIN: {isin}[/dim]" if isin else ""))

    if not refresh and has_cache(ticker):
        age = get_cache_age_hours(ticker)
        age_str = f"{age:.1f}h ago" if age is not None else "unknown age"
        console.print(f"[bold green]Using cached data[/] [dim](fetched {age_str})[/]")
        cached = load_cached_report(ticker)
        if cached:
            try:
                report = _dict_to_report(cached)
            except Exception as exc:
                console.print(f"[yellow]Cached data is corrupt ({exc}), re-fetching...[/]")
            else:
                if isin and report.profile.isin is None:
                    report.profile.isin = isin
                console.print(
                    f"[green]{report.profile.name}[/] -- "
                    f"{report.profile.tier.value}  {report.profile.stage.value}"
                )
                _notify("complete", report)
                return report

    if refresh:
        console.print("[yellow]Refreshing data from network...[/]")

    console.print("[cyan]Fetching company profile...[/]")
    info = fetch_info(ticker)
    profile = fetch_company_profile(ticker, info=info)
    profile.isin = isin

    if not profile.isin:
        try:
            import yfinance as yf
            fetched_isin = yf.Ticker(ticker).isin
            if fetched_isin and fetched_isin != "-":
                profile.isin = fetched_isin
        except Exception:
            pass

    tier = classify_tier(profile.market_cap)
    profile.tier = tier
    stage = classify_stage(profile.description, info.get("totalRevenue"), info)
    profile.stage = stage
    profile.primary_commodity = classify_commodity(profile.description, profile.industry)
    profile.jurisdiction_tier = classify_jurisdiction(profile.country, profile.description)
    if profile.country:
        profile.jurisdiction_country = profile.country

    console.print(
        f"[green]{profile.name}[/] -- {profile.sector or 'N/A'} / {profile.industry or 'N/A'}"
        f"  [bold][{_tier_color(tier)}]{tier.value}[/]"
        f"  [{_stage_color(stage)}]{stage.value}[/]"
    )

    # Validate sector — refuse to analyze non-energy companies
    _validate_sector(profile)

    if profile.primary_commodity.value != "Other":
        console.print(f"[cyan]Primary Commodity:[/] {profile.primary_commodity.value}")
    console.print(f"[cyan]Jurisdiction Risk:[/] {profile.jurisdiction_tier.value}")

    report = AnalysisReport(profile=profile)
    _notify("profile", report)

    console.print("[cyan]Fetching financial statements...[/]")
    statements = fetch_financial_statements(ticker)
    console.print(f"[green]Retrieved {len(statements)} annual periods[/]")
    report.financials = statements
    _notify("financials", report)

    console.print("[cyan]Calculating metrics...[/]")
    report.valuation = calc_valuation(info, statements, tier, stage)
    _notify("valuation", report)
    report.profitability = calc_profitability(info, statements, tier, stage)
    _notify("profitability", report)
    report.solvency = calc_solvency(info, statements, tier, stage)
    _notify("solvency", report)
    report.growth = calc_growth(statements, tier, stage)
    _notify("growth", report)
    report.efficiency = calc_efficiency(info, statements, tier)
    report.share_structure = calc_share_structure(info, statements, report.growth, tier, stage)
    _notify("share_structure", report)
    report.energy_quality = calc_energy_quality(
        report.profitability, report.growth, report.solvency,
        report.share_structure, statements, info, tier, stage,
    )
    _notify("energy_quality", report)
    report.intrinsic_value = calc_intrinsic_value(info, statements, report.growth, report.solvency, tier, stage)
    _notify("intrinsic_value", report)

    # Market intelligence (insider activity, analysts, short interest, technicals)
    console.print("[cyan]Gathering market intelligence...[/]")
    try:
        import yfinance as yf
        ticker_obj = yf.Ticker(ticker)
        report.market_intelligence = calc_market_intelligence(
            info, ticker_obj, report.solvency, report.share_structure,
            report.growth, tier, stage,
        )
        _notify("market_intelligence", report)
    except Exception as exc:
        console.print(f"[yellow]Market intelligence failed: {exc}[/]")

    _ticker, _max = ticker, max_filings
    with ThreadPoolExecutor(max_workers=2) as pool:
        filings_future = pool.submit(lambda: fetch_sec_filings(_ticker)) if download_reports else None
        news_future = pool.submit(lambda: fetch_all_news(_ticker, profile.name)) if download_news else None

        if download_reports:
            console.print("[cyan]Fetching SEC/SEDAR filings...[/]")
        if download_news:
            console.print("[cyan]Fetching news...[/]")

        if filings_future is not None:
            try:
                fl = filings_future.result()
                console.print(f"[green]Found {len(fl)} filings[/]")
                if fl:
                    console.print(f"[cyan]Downloading top {_max} filings...[/]")
                    download_top_filings(_ticker, fl, max_count=_max)
                report.filings = fl
                _notify("filings", report)
            except Exception as exc:
                console.print(f"[yellow]Filings fetch failed: {exc}[/]")
        if news_future is not None:
            try:
                nw = news_future.result()
                console.print(f"[green]Found {len(nw)} articles[/]")
                report.news = nw
                _notify("news", report)
            except Exception as exc:
                console.print(f"[yellow]News fetch failed: {exc}[/]")

    _notify("conclusion", report)

    console.print("[cyan]Saving analysis...[/]")
    path = save_analysis_report(ticker, _report_to_dict(report))
    console.print(f"[bold green]Analysis saved to:[/] {path}")
    _notify("complete", report)
    return report


def _report_to_dict(report: AnalysisReport) -> dict:
    def _dc(obj):
        if obj is None:
            return None
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            return {k: _dc(v) for k, v in dataclasses.asdict(obj).items()}
        if isinstance(obj, list):
            return [_dc(i) for i in obj]
        return obj
    return _dc(report)


def _dict_to_report(d: dict) -> AnalysisReport:
    profile = _build_dc(CompanyProfile, d.get("profile", {}))
    profile.tier = _parse_tier(d.get("profile", {}).get("tier", ""))
    profile.stage = _parse_stage(d.get("profile", {}).get("stage", ""))

    def _maybe(cls, key):
        raw = d.get(key)
        return _build_dc(cls, raw) if raw is not None else None

    return AnalysisReport(
        profile=profile,
        valuation=_maybe(ValuationMetrics, "valuation"),
        profitability=_maybe(ProfitabilityMetrics, "profitability"),
        solvency=_maybe(SolvencyMetrics, "solvency"),
        growth=_maybe(GrowthMetrics, "growth"),
        efficiency=_maybe(EfficiencyMetrics, "efficiency"),
        energy_quality=_maybe(EnergyQualityIndicators, "energy_quality"),
        intrinsic_value=_maybe(IntrinsicValue, "intrinsic_value"),
        share_structure=_maybe(ShareStructure, "share_structure"),
        market_intelligence=_maybe(MarketIntelligence, "market_intelligence"),
        financials=[_build_dc(FinancialStatement, s) for s in d.get("financials", [])],
        filings=[_build_dc(Filing, f) for f in d.get("filings", [])],
        news=[_build_dc(NewsArticle, n) for n in d.get("news", [])],
        fetched_at=d.get("fetched_at", ""),
    )


def _build_dc(cls, data: dict):
    import dataclasses as dc
    field_names = {f.name for f in dc.fields(cls)}
    return cls(**{k: v for k, v in data.items() if k in field_names})


def _parse_tier(raw) -> CompanyTier:
    if isinstance(raw, CompanyTier):
        return raw
    for t in CompanyTier:
        if t.value == str(raw) or t.name == str(raw):
            return t
    return CompanyTier.NANO


def _parse_stage(raw) -> CompanyStage:
    if isinstance(raw, CompanyStage):
        return raw
    for s in CompanyStage:
        if s.value == str(raw) or s.name == str(raw):
            return s
    return CompanyStage.GRASSROOTS


def _tier_color(tier) -> str:
    return {CompanyTier.MEGA: "bold green", CompanyTier.LARGE: "green", CompanyTier.MID: "cyan",
            CompanyTier.SMALL: "yellow", CompanyTier.MICRO: "#ff8800", CompanyTier.NANO: "bold red"}.get(tier, "white")


def _stage_color(stage) -> str:
    return {CompanyStage.PRODUCER: "bold green", CompanyStage.ROYALTY: "bold green",
            CompanyStage.DEVELOPER: "cyan", CompanyStage.EXPLORER: "yellow",
            CompanyStage.GRASSROOTS: "#ff8800"}.get(stage, "white")
