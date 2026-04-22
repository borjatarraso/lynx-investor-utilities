"""Tests for the sector validation gate (utilities sector)."""

import pytest
from lynx_utilities.core.analyzer import _validate_sector, SectorMismatchError
from lynx_utilities.models import CompanyProfile


class TestSectorValidation:
    """Sector validation blocks non-utility companies."""

    def _profile(self, ticker="T", sector=None, industry=None, desc=None):
        return CompanyProfile(ticker=ticker, name=f"{ticker} Corp",
                              sector=sector, industry=industry, description=desc)

    # --- Should ALLOW ---
    def test_utilities_sector(self):
        _validate_sector(self._profile(sector="Utilities", industry="Utilities—Regulated Electric"))

    def test_utilities_regulated_gas(self):
        _validate_sector(self._profile(sector="Utilities", industry="Utilities—Regulated Gas"))

    def test_utilities_regulated_water(self):
        _validate_sector(self._profile(sector="Utilities", industry="Utilities—Regulated Water"))

    def test_utilities_diversified(self):
        _validate_sector(self._profile(sector="Utilities", industry="Utilities—Diversified"))

    def test_utilities_renewable(self):
        _validate_sector(self._profile(sector="Utilities", industry="Utilities—Renewable"))

    def test_utilities_ipp(self):
        _validate_sector(self._profile(sector="Utilities", industry="Independent Power Producers & Traders"))

    def test_multi_utilities(self):
        _validate_sector(self._profile(sector="Utilities", industry="Multi-Utilities"))

    def test_rate_base_in_description(self):
        _validate_sector(self._profile(sector="Other", industry="Other",
                                       desc="Regulated electric utility earning an allowed ROE on a rate base"))

    def test_yieldco_in_description(self):
        _validate_sector(self._profile(sector="Other", industry="Other",
                                       desc="YieldCo owning contracted wind and solar assets under long-term PPAs"))

    def test_ipp_in_description(self):
        _validate_sector(self._profile(sector="Other", industry="Other",
                                       desc="Independent power producer selling generation into wholesale power markets"))

    # --- Should BLOCK ---
    def test_technology_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Technology", industry="Consumer Electronics"))

    def test_financial_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Financial Services", industry="Banks"))

    def test_healthcare_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Healthcare", industry="Drug Manufacturers"))

    def test_consumer_cyclical_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Consumer Cyclical", industry="Auto Manufacturers"))

    def test_real_estate_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Real Estate", industry="REIT"))

    def test_energy_oil_gas_blocked(self):
        """An oil & gas E&P is not a utility — use lynx-energy instead."""
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Energy", industry="Oil & Gas E&P"))

    def test_all_none_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile())

    def test_empty_strings_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="", industry="", desc=""))

    def test_generic_power_tool_blocked(self):
        """A consumer power-tool maker is not a utility."""
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(
                sector="Industrials", industry="Tools & Accessories",
                desc="Designs and manufactures consumer power tools"))

    def test_app_store_blocked(self):
        """AAPL is not a utility."""
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(
                sector="Technology", industry="Consumer Electronics",
                desc="App Store that allows customers to discover apps"))

    def test_error_message_content(self):
        with pytest.raises(SectorMismatchError, match="outside the scope"):
            _validate_sector(self._profile(sector="Technology", industry="Software"))

    def test_generic_water_bottler_blocked(self):
        """A bottled-water beverage company is NOT a water utility."""
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(
                sector="Consumer Defensive", industry="Beverages—Non-Alcoholic",
                desc="Sells bottled water and flavoured beverages to retail customers"))

    def test_industrial_generation_equipment_blocked(self):
        """A manufacturer of generator equipment is NOT a utility."""
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(
                sector="Industrials", industry="Specialty Industrial Machinery",
                desc="Manufactures backup generator sets sold through distributors"))

    def test_electric_vehicle_blocked(self):
        """An EV maker is not a utility."""
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(
                sector="Consumer Cyclical", industry="Auto Manufacturers",
                desc="Electric vehicles and battery systems for consumer markets"))

    def test_nuclear_fleet_allowed(self):
        """A company operating a nuclear generation fleet is a utility."""
        _validate_sector(self._profile(sector="Other", industry="Other",
                                       desc="Operates nuclear generation fleet and regulated electric distribution"))

    def test_water_wastewater_allowed(self):
        """A water and wastewater operator is a utility."""
        _validate_sector(self._profile(sector="Other", industry="Other",
                                       desc="Regulated water and wastewater services in 14 US states"))

    def test_error_suggests_another_agent(self):
        """Wrong-sector warning appends a 'use lynx-investor-*' line."""
        with pytest.raises(SectorMismatchError) as exc:
            _validate_sector(self._profile(
                sector="Healthcare", industry="Biotechnology"))
        message = str(exc.value)
        assert "Suggestion" in message
        assert "lynx-investor-healthcare" in message

    def test_error_never_suggests_self(self):
        """The suggestion never points back to this agent itself."""
        with pytest.raises(SectorMismatchError) as exc:
            _validate_sector(self._profile(
                sector="Technology", industry="Software"))
        message = str(exc.value)
        assert "use 'lynx-investor-utilities'" not in message
