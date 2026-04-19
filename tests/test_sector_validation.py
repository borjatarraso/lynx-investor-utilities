"""Tests for the sector validation gate."""

import pytest
from lynx_energy.core.analyzer import _validate_sector, SectorMismatchError
from lynx_energy.models import CompanyProfile


class TestSectorValidation:
    """Sector validation blocks non-energy companies."""

    def _profile(self, ticker="T", sector=None, industry=None, desc=None):
        return CompanyProfile(ticker=ticker, name=f"{ticker} Corp",
                              sector=sector, industry=industry, description=desc)

    # --- Should ALLOW ---
    def test_energy_sector(self):
        _validate_sector(self._profile(sector="Energy", industry="Oil & Gas E&P"))

    def test_energy_uranium(self):
        _validate_sector(self._profile(sector="Energy", industry="Uranium"))

    def test_oil_gas_exploration(self):
        _validate_sector(self._profile(sector="Energy", industry="Oil & Gas Exploration & Production"))

    def test_oil_gas_integrated(self):
        _validate_sector(self._profile(sector="Energy", industry="Oil & Gas Integrated"))

    def test_oil_gas_midstream(self):
        _validate_sector(self._profile(sector="Energy", industry="Oil & Gas Midstream"))

    def test_coal_industry(self):
        _validate_sector(self._profile(sector="Energy", industry="Thermal Coal"))

    def test_drilling_in_description(self):
        _validate_sector(self._profile(sector="Other", industry="Other",
                                       desc="Active drilling program on property"))

    def test_oil_in_description(self):
        _validate_sector(self._profile(sector="Other", industry="Other",
                                       desc="Crude oil exploration and production company"))

    def test_pipeline_in_description(self):
        _validate_sector(self._profile(sector="Other", industry="Other",
                                       desc="Midstream pipeline and natural gas processing company"))

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

    def test_all_none_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile())

    def test_empty_strings_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="", industry="", desc=""))

    def test_lithium_ion_battery_blocked(self):
        """TSLA mentions 'lithium-ion battery' but is not an energy company."""
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(
                sector="Consumer Cyclical", industry="Auto Manufacturers",
                desc="Electric vehicles with lithium-ion battery energy storage"))

    def test_app_store_blocked(self):
        """AAPL is not an energy company."""
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(
                sector="Technology", industry="Consumer Electronics",
                desc="App Store that allows customers to discover apps"))

    def test_error_message_content(self):
        with pytest.raises(SectorMismatchError, match="outside the scope"):
            _validate_sector(self._profile(sector="Technology", industry="Software"))
