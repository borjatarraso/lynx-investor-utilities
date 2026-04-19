"""Unit tests for data models and classification functions."""

import pytest
from lynx_energy.models import (
    CompanyProfile, CompanyStage, CompanyTier, Commodity,
    JurisdictionTier, Relevance, AnalysisReport,
    ValuationMetrics, SolvencyMetrics, GrowthMetrics,
    EnergyQualityIndicators, ShareStructure, MarketIntelligence,
    FinancialStatement, AnalysisConclusion,
    classify_tier, classify_stage, classify_commodity, classify_jurisdiction,
)


class TestClassifyTier:
    def test_mega_cap(self):
        assert classify_tier(300_000_000_000) == CompanyTier.MEGA

    def test_large_cap(self):
        assert classify_tier(50_000_000_000) == CompanyTier.LARGE

    def test_mid_cap(self):
        assert classify_tier(5_000_000_000) == CompanyTier.MID

    def test_small_cap(self):
        assert classify_tier(1_000_000_000) == CompanyTier.SMALL

    def test_micro_cap(self):
        assert classify_tier(100_000_000) == CompanyTier.MICRO

    def test_nano_cap(self):
        assert classify_tier(10_000_000) == CompanyTier.NANO

    def test_none_returns_nano(self):
        assert classify_tier(None) == CompanyTier.NANO

    def test_zero_returns_nano(self):
        assert classify_tier(0) == CompanyTier.NANO

    def test_negative_returns_nano(self):
        assert classify_tier(-100) == CompanyTier.NANO


class TestClassifyStage:
    def test_producer_with_revenue(self):
        assert classify_stage("oil production operations with netback", 50_000_000) == CompanyStage.PRODUCER

    def test_developer(self):
        assert classify_stage("feasibility study complete", 0) == CompanyStage.DEVELOPER

    def test_developer_exploration_and_development(self):
        assert classify_stage("exploration and development of uranium", 5_000_000) == CompanyStage.DEVELOPER

    def test_explorer(self):
        assert classify_stage("NI 43-101 resource estimate with inferred resource", 0) == CompanyStage.EXPLORER

    def test_grassroots(self):
        assert classify_stage("early stage exploration drill program", 0) == CompanyStage.GRASSROOTS

    def test_royalty(self):
        assert classify_stage("royalty and streaming company", 20_000_000) == CompanyStage.ROYALTY

    def test_none_description(self):
        assert classify_stage(None, None) == CompanyStage.GRASSROOTS

    def test_empty_description(self):
        assert classify_stage("", 0) == CompanyStage.GRASSROOTS

    def test_industry_hint(self):
        assert classify_stage("company overview", 0, {"industry": "Oil & Gas E&P"}) == CompanyStage.EXPLORER


class TestClassifyCommodity:
    def test_uranium(self):
        assert classify_commodity("uranium u3o8 exploration", "Uranium") == Commodity.URANIUM

    def test_crude_oil(self):
        assert classify_commodity("crude oil production petroleum", "Oil & Gas E&P") == Commodity.CRUDE_OIL

    def test_natural_gas(self):
        assert classify_commodity("natural gas shale gas production", "Oil & Gas E&P") == Commodity.NATURAL_GAS

    def test_lng(self):
        assert classify_commodity("liquefied natural gas lng export", None) == Commodity.LNG

    def test_coal(self):
        assert classify_commodity("thermal coal mining operations", "Thermal Coal") == Commodity.COAL

    def test_hydrogen(self):
        assert classify_commodity("green hydrogen electrolysis project", None) == Commodity.HYDROGEN

    def test_renewable(self):
        assert classify_commodity("solar wind renewable energy", None) == Commodity.RENEWABLE

    def test_other_when_no_match(self):
        assert classify_commodity("generic company", None) == Commodity.OTHER

    def test_none_inputs(self):
        assert classify_commodity(None, None) == Commodity.OTHER

    def test_uranium_not_confused(self):
        assert classify_commodity("uranium exploration in Saskatchewan", "Uranium") == Commodity.URANIUM


class TestClassifyJurisdiction:
    def test_canada_tier1(self):
        assert classify_jurisdiction("Canada") == JurisdictionTier.TIER_1

    def test_us_tier1(self):
        assert classify_jurisdiction("United States") == JurisdictionTier.TIER_1

    def test_australia_tier1(self):
        assert classify_jurisdiction("Australia") == JurisdictionTier.TIER_1

    def test_mexico_tier2(self):
        assert classify_jurisdiction("Mexico") == JurisdictionTier.TIER_2

    def test_brazil_tier2(self):
        assert classify_jurisdiction("Brazil") == JurisdictionTier.TIER_2

    def test_unknown_tier3(self):
        assert classify_jurisdiction("SomeCountry") == JurisdictionTier.TIER_3

    def test_none_unknown(self):
        assert classify_jurisdiction(None) == JurisdictionTier.UNKNOWN


class TestDataModels:
    def test_analysis_report_defaults(self):
        r = AnalysisReport(profile=CompanyProfile(ticker="TEST", name="Test"))
        assert r.valuation is None
        assert r.market_intelligence is None
        assert r.financials == []
        assert r.fetched_at != ""

    def test_company_profile_defaults(self):
        p = CompanyProfile(ticker="X", name="X Corp")
        assert p.tier == CompanyTier.NANO
        assert p.stage == CompanyStage.GRASSROOTS
        assert p.primary_commodity == Commodity.OTHER
        assert p.jurisdiction_tier == JurisdictionTier.UNKNOWN

    def test_solvency_metrics_defaults(self):
        s = SolvencyMetrics()
        assert s.cash_runway_years is None
        assert s.burn_as_pct_of_market_cap is None

    def test_market_intelligence_defaults(self):
        mi = MarketIntelligence()
        assert mi.insider_transactions == []
        assert mi.risk_warnings == []
        assert mi.disclaimers == []
