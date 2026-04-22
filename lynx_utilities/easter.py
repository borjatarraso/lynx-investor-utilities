"""Easter-egg shim over :mod:`lynx_investor_core.easter`.

Binds utilities-specific labels and fortune quotes so call sites stay
unchanged. Also re-exports the legacy constants (LYNX_ASCII, WOLF_ASCII,
BULL_ASCII, PICKAXE_ASCII, FORTUNE_QUOTES, ROCKET_ASCII) for callers that
reference them directly (e.g. the Textual TUI).
"""

from __future__ import annotations

from lynx_investor_core import easter as _core_easter
from lynx_investor_core.easter import (  # noqa: F401
    BULL_ASCII,
    GENERIC_FORTUNES,
    ROCKET_ASCII,
    WOLF_ASCII,
)

_UTILITIES_FORTUNES = (
    '"Electricity is really just organized lightning." \u2014 George Carlin',
    '"A utility is a promise: the lights stay on." \u2014 Utilities proverb',
    '"The grid is the largest machine ever built by mankind." \u2014 IEEE observation',
    '"Rate base compounds quietly; the market eventually notices." \u2014 Buy-side mantra',
)

FORTUNE_QUOTES = tuple(GENERIC_FORTUNES) + _UTILITIES_FORTUNES

_EGG = _core_easter.AgentEasterEgg(
    label="Utilities Analysis",
    sublabel="Utilities Sector Research",
    banner_prog="lynx-utilities",
    extra_fortunes=_UTILITIES_FORTUNES,
)

# Pre-rendered ASCII variants (legacy callers that import these directly).
LYNX_ASCII = _core_easter._lynx_ascii(_EGG.label)
PICKAXE_ASCII = _core_easter._pickaxe_ascii(_EGG.sublabel)


def rich_matrix(console, duration: float = 3.0) -> None:
    _core_easter.rich_matrix(console, duration=duration)


def rich_fortune(console) -> None:
    _core_easter.rich_fortune(console, _EGG)


def rich_rocket(console) -> None:
    _core_easter.rich_rocket(console)


def rich_lynx(console) -> None:
    _core_easter.rich_lynx(console, _EGG)


def tk_fireworks(root) -> None:
    _core_easter.tk_fireworks(root, _EGG)


def tk_rainbow_title(root, count: int = 20) -> None:
    _core_easter.tk_rainbow_title(root, _EGG, count=count)
