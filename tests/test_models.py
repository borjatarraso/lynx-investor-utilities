"""Unit tests for data models and classification functions (utilities sector)."""

import pytest
from lynx_utilities.models import (
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
        assert classify_stage("regulated electric utility with rate base", 500_000_000) == CompanyStage.PRODUCER

    def test_developer(self):
        assert classify_stage("wind farm under construction, commercial operation date 2027", 0) == CompanyStage.DEVELOPER

    def test_developer_pre_operational(self):
        assert classify_stage("pre-operational solar project nearing COD", 5_000_000) == CompanyStage.DEVELOPER

    def test_explorer(self):
        assert classify_stage("development pipeline includes 3 GW of permitted projects with PPA signed", 0) == CompanyStage.EXPLORER

    def test_grassroots(self):
        assert classify_stage("early stage development of greenfield solar site, resource assessment", 0) == CompanyStage.GRASSROOTS

    def test_royalty_yieldco(self):
        assert classify_stage("yieldco operating a portfolio of contracted wind and solar assets", 200_000_000) == CompanyStage.ROYALTY

    def test_integrated_multi_utility_is_producer(self):
        """Multi-utility with electric and gas operations should classify as Producer."""
        desc = "Operates regulated electric utility and gas distribution across 4 states."
        assert classify_stage(desc, 15_000_000_000) == CompanyStage.PRODUCER

    def test_revenue_without_keywords_defaults_producer(self):
        """Revenue-generating company with no stage keywords defaults to Operating Utility."""
        assert classify_stage("generic utility company", 500_000_000) == CompanyStage.PRODUCER

    def test_none_description(self):
        assert classify_stage(None, None) == CompanyStage.GRASSROOTS

    def test_empty_description(self):
        assert classify_stage("", 0) == CompanyStage.GRASSROOTS

    def test_industry_hint(self):
        assert classify_stage("company overview", 0, {"industry": "Utilities—Regulated Electric"}) == CompanyStage.EXPLORER


class TestClassifyCommodity:
    def test_regulated_electric(self):
        assert classify_commodity("regulated electric utility serving 4 million customers", "Utilities—Regulated Electric") == Commodity.REGULATED_ELECTRIC

    def test_merchant_power(self):
        assert classify_commodity("independent power producer selling into wholesale markets", "Utilities—Independent Power Producers") == Commodity.MERCHANT_POWER

    def test_regulated_gas(self):
        assert classify_commodity("natural gas utility local distribution company", "Utilities—Regulated Gas") == Commodity.REGULATED_GAS

    def test_water(self):
        assert classify_commodity("water and wastewater services across 14 states", "Utilities—Regulated Water") == Commodity.WATER

    def test_renewable_power(self):
        assert classify_commodity("utility-scale solar and wind power portfolio", None) == Commodity.RENEWABLE_POWER

    def test_nuclear(self):
        assert classify_commodity("nuclear generation fleet with 5 reactors", None) == Commodity.NUCLEAR_GENERATION

    def test_multi_utility(self):
        assert classify_commodity("multi-utility combining electric and gas services", None) == Commodity.MULTI_UTILITY

    def test_other_when_no_match(self):
        assert classify_commodity("generic company", None) == Commodity.OTHER

    def test_none_inputs(self):
        assert classify_commodity(None, None) == Commodity.OTHER


class TestClassifyJurisdiction:
    def test_canada_tier1(self):
        assert classify_jurisdiction("Canada") == JurisdictionTier.TIER_1

    def test_us_tier1(self):
        assert classify_jurisdiction("United States") == JurisdictionTier.TIER_1

    def test_australia_tier1(self):
        assert classify_jurisdiction("Australia") == JurisdictionTier.TIER_1

    def test_germany_tier1(self):
        assert classify_jurisdiction("Germany") == JurisdictionTier.TIER_1

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
