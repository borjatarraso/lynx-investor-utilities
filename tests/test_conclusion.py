"""Unit tests for the conclusion engine."""

import pytest
from lynx_energy.models import (
    AnalysisReport, CompanyProfile, CompanyStage, CompanyTier,
    ValuationMetrics, SolvencyMetrics, GrowthMetrics,
    EnergyQualityIndicators, ShareStructure,
)
from lynx_energy.core.conclusion import generate_conclusion


@pytest.fixture
def minimal_report():
    return AnalysisReport(profile=CompanyProfile(ticker="TEST", name="Test Corp"))


@pytest.fixture
def explorer_report():
    p = CompanyProfile(ticker="EXP", name="Explorer Corp", market_cap=100_000_000)
    p.tier = CompanyTier.MICRO
    p.stage = CompanyStage.EXPLORER
    r = AnalysisReport(profile=p)
    r.valuation = ValuationMetrics(pb_ratio=0.8, cash_to_market_cap=0.4)
    r.solvency = SolvencyMetrics(cash_runway_years=3.5, current_ratio=4.0,
                                  debt_to_equity=0.1, cash_burn_rate=-5_000_000)
    r.growth = GrowthMetrics(shares_growth_yoy=0.03)
    r.energy_quality = EnergyQualityIndicators(quality_score=65.0,
                                               competitive_position="Viable Position")
    r.share_structure = ShareStructure(fully_diluted_shares=80_000_000,
                                       insider_ownership_pct=0.15)
    return r


class TestGenerateConclusion:
    def test_minimal_report_produces_verdict(self, minimal_report):
        c = generate_conclusion(minimal_report)
        assert c.verdict in ["Strong Buy", "Buy", "Hold", "Caution", "Avoid"]
        assert 0 <= c.overall_score <= 100
        assert c.summary != ""

    def test_verdict_thresholds(self, minimal_report):
        c = generate_conclusion(minimal_report)
        if c.overall_score >= 75:
            assert c.verdict == "Strong Buy"
        elif c.overall_score >= 60:
            assert c.verdict == "Buy"
        elif c.overall_score >= 45:
            assert c.verdict == "Hold"
        elif c.overall_score >= 30:
            assert c.verdict == "Caution"
        else:
            assert c.verdict == "Avoid"

    def test_explorer_has_stage_note(self, explorer_report):
        c = generate_conclusion(explorer_report)
        assert c.stage_note != ""
        assert "Explorer" in c.stage_note or "EV/resource" in c.stage_note

    def test_category_scores_present(self, explorer_report):
        c = generate_conclusion(explorer_report)
        assert "valuation" in c.category_scores
        assert "profitability" in c.category_scores
        assert "solvency" in c.category_scores
        assert "growth" in c.category_scores
        assert "energy_quality" in c.category_scores

    def test_screening_checklist_present(self, explorer_report):
        c = generate_conclusion(explorer_report)
        assert isinstance(c.screening_checklist, dict)
        assert "cash_runway_18m" in c.screening_checklist
        assert "insider_ownership" in c.screening_checklist

    def test_good_explorer_scores_well(self, explorer_report):
        c = generate_conclusion(explorer_report)
        assert c.overall_score >= 45  # At least Hold

    def test_strengths_detected(self, explorer_report):
        c = generate_conclusion(explorer_report)
        assert len(c.strengths) >= 1
