"""Lynx Utilities — Fundamental analysis for regulated and merchant utility companies."""

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

__version__ = "5.4"  # lynx-investor-utilities version (independent of core)

APP_NAME = "Lynx Utilities Analysis"
APP_SHORT_NAME = "Utilities Analysis"
APP_TAGLINE = "Utilities Sector Analysis"
APP_SCOPE = "the utilities sector"
PROG_NAME = "lynx-utilities"
PACKAGE_NAME = "lynx_utilities"
USER_AGENT_PRODUCT = "LynxUtilities"
NEWS_SECTOR_KEYWORD = "utilities stock"

TICKER_SUGGESTIONS = (
    "  - For US regulated utilities, try: NEE, DUK, SO, AEP, XEL",
    "  - For US water utilities, try: AWK, WTRG, AWR",
    "  - For IPP / renewable utilities, try: NRG, VST, BEP, CWEN",
    "  - For European utilities, try: IBE.MC, ENEL.MI, NG.L, EDF.PA",
    "  - You can also type the full company name: 'NextEra Energy'",
)

DESCRIPTION = (
    "Fundamental analysis specialized for regulated electric, gas, "
    "water, and multi-utility companies as well as independent power "
    "producers and YieldCos. Evaluates utilities across all stages "
    "from early-stage renewable developers to mature regulated "
    "operators using utility-specific metrics: rate base growth, "
    "allowed vs earned ROE, FFO/Debt, FFO interest coverage, "
    "dividend coverage, regulatory jurisdiction scoring, capex "
    "intensity, generation mix, and more.\n\n"
    "Part of the Lince Investor Suite."
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_logo_ascii() -> str:
    """Load the ASCII logo from img/logo_ascii.txt."""
    from lynx_investor_core.logo import load_logo_ascii
    return load_logo_ascii(Path(__file__).resolve().parent) or "  L Y N X   U T I L I T I E S   A N A L Y S I S\n"


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
