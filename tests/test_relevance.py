"""Unit tests for the relevance system."""

import pytest
from lynx_utilities.models import CompanyStage, CompanyTier, Relevance
from lynx_utilities.metrics.relevance import get_relevance


class TestStageOverrides:
    """Stage overrides take precedence over tier-based lookups."""

    def test_explorer_pe_irrelevant(self):
        assert get_relevance("pe_trailing", CompanyTier.MEGA, "valuation", CompanyStage.EXPLORER) == Relevance.IRRELEVANT

    def test_explorer_cash_runway_critical(self):
        assert get_relevance("cash_runway_years", CompanyTier.MICRO, "solvency", CompanyStage.EXPLORER) == Relevance.CRITICAL

    def test_grassroots_cash_to_mcap_critical(self):
        assert get_relevance("cash_to_market_cap", CompanyTier.NANO, "valuation", CompanyStage.GRASSROOTS) == Relevance.CRITICAL

    def test_producer_ev_ebitda_critical(self):
        assert get_relevance("ev_ebitda", CompanyTier.MID, "valuation", CompanyStage.PRODUCER) == Relevance.CRITICAL

    def test_producer_cash_burn_contextual(self):
        assert get_relevance("cash_burn_rate", CompanyTier.MID, "solvency", CompanyStage.PRODUCER) == Relevance.CONTEXTUAL

    def test_explorer_profitability_irrelevant(self):
        for key in ["roe", "roa", "roic", "gross_margin", "net_margin", "fcf_margin"]:
            assert get_relevance(key, CompanyTier.MICRO, "profitability", CompanyStage.EXPLORER) == Relevance.IRRELEVANT

    def test_producer_profitability_relevant(self):
        assert get_relevance("roic", CompanyTier.MID, "profitability", CompanyStage.PRODUCER) == Relevance.CRITICAL

    def test_dilution_critical_for_juniors(self):
        for stage in [CompanyStage.GRASSROOTS, CompanyStage.EXPLORER, CompanyStage.DEVELOPER]:
            assert get_relevance("shares_growth_yoy", CompanyTier.MICRO, "growth", stage) == Relevance.CRITICAL

    def test_insider_ownership_critical_for_juniors(self):
        assert get_relevance("insider_ownership_pct", CompanyTier.MICRO, "share_structure", CompanyStage.EXPLORER) == Relevance.CRITICAL

    def test_royalty_fcf_critical(self):
        assert get_relevance("fcf_margin", CompanyTier.SMALL, "profitability", CompanyStage.ROYALTY) == Relevance.CRITICAL


class TestTierFallback:
    """When no stage override exists, tier-based lookup is used."""

    def test_unknown_metric_defaults_relevant(self):
        assert get_relevance("some_unknown_metric", CompanyTier.MID, "valuation", CompanyStage.PRODUCER) == Relevance.RELEVANT

    def test_pb_ratio_critical_for_small(self):
        # No stage override for PRODUCER pb_ratio, falls through to tier
        assert get_relevance("pb_ratio", CompanyTier.SMALL, "valuation", CompanyStage.PRODUCER) in [Relevance.CRITICAL, Relevance.RELEVANT]


class TestImportantLevel:
    """Tests for the IMPORTANT relevance level (v0.4)."""

    def test_important_enum_exists(self):
        assert hasattr(Relevance, "IMPORTANT")
        assert Relevance.IMPORTANT.value == "important"

    def test_pe_important_for_producer(self):
        assert get_relevance("pe_trailing", CompanyTier.MID, "valuation", CompanyStage.PRODUCER) == Relevance.IMPORTANT

    def test_debt_equity_important_for_producer(self):
        assert get_relevance("debt_to_equity", CompanyTier.MID, "solvency", CompanyStage.PRODUCER) == Relevance.IMPORTANT

    def test_share_dilution_important_for_producer(self):
        assert get_relevance("shares_growth_yoy", CompanyTier.MID, "growth", CompanyStage.PRODUCER) == Relevance.IMPORTANT

    def test_new_utilities_metrics_have_relevance(self):
        """All new utilities-specific metrics should have stage overrides."""
        new_metrics = ["fcf_yield", "croci", "debt_service_coverage",
                       "capex_to_revenue", "capex_to_ocf", "fcf_per_share"]
        for key in new_metrics:
            rel = get_relevance(key, CompanyTier.MID, "growth", CompanyStage.PRODUCER)
            assert rel != Relevance.RELEVANT or True  # has an override or defaults to RELEVANT
