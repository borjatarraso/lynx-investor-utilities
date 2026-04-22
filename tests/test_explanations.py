"""Unit tests for metric explanations."""

import pytest
from lynx_utilities.metrics.explanations import (
    get_explanation, list_metrics, get_section_explanation,
    get_conclusion_explanation, SECTION_EXPLANATIONS, CONCLUSION_METHODOLOGY,
)


class TestGetExplanation:
    def test_known_metric(self):
        e = get_explanation("cash_to_market_cap")
        assert e is not None
        assert e.full_name == "Cash-to-Market-Cap Ratio"
        assert e.category == "valuation"

    def test_unknown_metric(self):
        assert get_explanation("nonexistent") is None

    def test_all_metrics_have_required_fields(self):
        for m in list_metrics():
            assert m.key != ""
            assert m.full_name != ""
            assert m.description != ""
            assert m.formula != ""
            assert m.category != ""

    def test_utilities_specific_metrics_exist(self):
        keys = [m.key for m in list_metrics()]
        assert "cash_to_market_cap" in keys
        assert "quality_score" in keys
        assert "shares_growth_yoy" in keys
        assert "dividend_coverage" in keys
        assert "dividend_payout_ratio" in keys
        assert "debt_service_coverage" in keys
        assert "capex_to_revenue" in keys

    def test_list_by_category(self):
        valuation = list_metrics("valuation")
        assert len(valuation) > 0
        assert all(m.category == "valuation" for m in valuation)


class TestSectionExplanations:
    def test_all_sections_have_title(self):
        for key, sec in SECTION_EXPLANATIONS.items():
            assert "title" in sec
            assert "description" in sec

    def test_utilities_quality_section_exists(self):
        sec = get_section_explanation("energy_quality")   # schema key kept for suite parity
        assert sec is not None
        assert "Utilities Quality" in sec["title"]

    def test_share_structure_section_exists(self):
        sec = get_section_explanation("share_structure")
        assert sec is not None

    def test_unknown_section(self):
        assert get_section_explanation("nonexistent") is None


class TestConclusionMethodology:
    def test_overall_exists(self):
        ce = get_conclusion_explanation("overall")
        assert ce is not None
        assert "utility quality" in ce["description"].lower()

    def test_unknown_category(self):
        assert get_conclusion_explanation("nonexistent") is None
