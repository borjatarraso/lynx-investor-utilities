"""Lynx Energy — Fundamental analysis for oil & gas, uranium, coal & energy companies."""

from pathlib import Path

# Suite-level constants come from lynx-investor-core (shared across every agent).
from lynx_investor_core import (
    LICENSE_NAME,
    LICENSE_TEXT,
    LICENSE_URL,
    SUITE_LABEL,
    SUITE_NAME,
    SUITE_VERSION,
    __author__,
    __author_email__,
    __license__,
    __year__,
)
from lynx_investor_core import storage as _core_storage

# Initialize the shared storage layer with this agent's project root so
# data/ and data_test/ live beside *this* package.
_core_storage.set_base_dir(Path(__file__).resolve().parent.parent)

# ---------------------------------------------------------------------------
# Agent-specific identity
# ---------------------------------------------------------------------------

__version__ = "2.0"  # lynx-investor-energy version (independent of core)

APP_NAME = "Lynx Energy Analysis"
APP_SHORT_NAME = "Energy Analysis"
APP_TAGLINE = "Energy Sector Analysis"
APP_SCOPE = "the energy sector"
PROG_NAME = "lynx-energy"
PACKAGE_NAME = "lynx_energy"
USER_AGENT_PRODUCT = "LynxEnergy"
NEWS_SECTOR_KEYWORD = "energy stock"

TICKER_SUGGESTIONS = (
    "  - For TSXV stocks, try: VET.TO, BTE.TO",
    "  - For TSX stocks, try: CVE.TO, ENB.TO",
    "  - For US stocks, try: XOM, OVV, DVN",
    "  - You can also type the full company name: 'Exxon Mobil'",
)

DESCRIPTION = (
    "Fundamental analysis specialized for oil & gas, uranium, coal, "
    "and energy companies. Evaluates companies across all stages from "
    "early exploration to production using energy-specific metrics: "
    "EV/BOE, reserve life, netback, breakeven price, F&D cost, "
    "cash runway, share structure analysis, and more.\n\n"
    "Part of the Lince Investor Suite."
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_logo_ascii() -> str:
    """Load the ASCII logo from img/logo_ascii.txt."""
    from lynx_investor_core.logo import load_logo_ascii
    return load_logo_ascii(Path(__file__).resolve().parent) or "  L Y N X   E N E R G Y   A N A L Y S I S\n"


def get_about_text() -> dict:
    """Return structured about information (uniform across agents)."""
    from lynx_investor_core.about import AgentMeta, build_about
    meta = AgentMeta(
        app_name=APP_NAME,
        short_name=APP_SHORT_NAME,
        tagline=APP_TAGLINE,
        package_name=PACKAGE_NAME,
        prog_name=PROG_NAME,
        version=__version__,
        description=DESCRIPTION,
        scope_description=APP_SCOPE,
    )
    about = build_about(meta, logo_ascii=get_logo_ascii())
    # Legacy key — some callers still reference about['logo'].
    about["logo"] = about["logo_ascii"]
    return about
