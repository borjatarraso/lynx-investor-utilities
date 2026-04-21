"""Easter-egg shim over :mod:`lynx_investor_core.easter`.

Binds energy-specific labels and fortune quotes so call sites stay unchanged.
Also re-exports the legacy constants (LYNX_ASCII, WOLF_ASCII, BULL_ASCII,
PICKAXE_ASCII, FORTUNE_QUOTES, ROCKET_ASCII) for callers that reference them
directly (e.g. the Textual TUI).
"""

from __future__ import annotations

from lynx_investor_core import easter as _core_easter
from lynx_investor_core.easter import (  # noqa: F401
    BULL_ASCII,
    GENERIC_FORTUNES,
    ROCKET_ASCII,
    WOLF_ASCII,
)

_ENERGY_FORTUNES = (
    '"The stone age did not end for lack of stone, and the oil age will end long before '
    'the world runs out of oil." \u2014 Sheikh Zaki Yamani',
    '"The cure for low prices is low prices." \u2014 Commodity proverb',
    '"Energy is the currency of the universe." \u2014 Energy proverb',
)

FORTUNE_QUOTES = tuple(GENERIC_FORTUNES) + _ENERGY_FORTUNES

_EGG = _core_easter.AgentEasterEgg(
    label="Energy Analysis",
    sublabel="Energy Sector Research",
    banner_prog="lynx-energy",
    extra_fortunes=_ENERGY_FORTUNES,
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
