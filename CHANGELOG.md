# Changelog

## 6.0.0 — 2026-04-26

**Major release synchronising the entire Lince Investor Suite.**

### What's new across the Suite

- **lynx-fund** — brand-new mutual / index fund analysis tool, rejecting
  ETFs and stocks at the resolver level. Surfaces share classes, loads,
  12b-1 fees, manager tenure, persistence, capital-gains tax drag, and
  20-rule passive-investor checklist with tailored tips.
- **lynx-compare-fund** — head-to-head comparison for two mutual / index
  funds. Adds a Boglehead-style Passive-Investor Verdict, plus warnings
  for active-vs-passive, UCITS, soft- / hard-close, and distribution-
  policy mismatches.
- **lynx-theme** — visual theme editor for the entire Suite (GUI + TUI
  only). Edit colours, fonts, alignment, bold / italic / underline /
  blink / marquee for 15 styled areas with live preview. Three built-in
  read-only reference themes (`lynx-mocha`, `lynx-latte`,
  `lynx-high-contrast`). Sets the default theme persisted to
  `$XDG_CONFIG_HOME/lynx-theme/default.json`.
- **i18n** — every Suite CLI now accepts `--language=us|es|it|de|fr|fa`
  and persists the user's choice to `$XDG_CONFIG_HOME/lynx/language.json`.
  GUI apps mount a small bottom-right language toggle (left-click
  cycles, right-click opens a chooser); TUI apps bind `g` to cycle.
  Honours `LYNX_LANG` for ad-hoc shells.
- **Author signature footer** — every txt / html / pdf export now ends
  with the Suite-wide author block: *Borja Tarraso
  &lt;borja.tarraso@member.fsf.org&gt;*. Provided by the new
  `lynx_investor_core.author_footer` module.

### Dashboard

- Two new APP launchables (Lynx Fund, Lynx Compare Fund, Lynx Theme),
  raising the catalogue to **8 apps + 11 sector agents = 19
  launchables**.
- Per-app launch dialect (`run_mode_dialect`, `ui_mode_flags`,
  `accepts_identifier`) so the launcher emits argv each app
  understands; lynx-theme + lynx-portfolio launch correctly from every
  mode.
- `--recommend` now rejects empty queries instead of silently passing.

### Bug fixes

- `__main__.py` of every fund / compare-fund / etf / compare-etf entry
  point now propagates `run_cli`'s return code so non-zero exits are
  visible to shell scripts and CI pipelines.
- Stale-install hygiene: pyproject editable installs now overwrite
  cached site-packages copies cleanly.
- Cosmetic clean-up: remaining "ETF" labels in fund / compare-fund
  GUI / TUI / interactive prompts → "Fund".
- Validation: empty positional ticker, missing second comparison
  ticker, and `--recommend ""` now exit non-zero with a clear message.


## [4.0] - 2026-04-23

Part of **Lince Investor Suite v4.0** coordinated release.

### Added
- URL-safety enforcement for every RSS-sourced news URL and every
  `webbrowser.open(...)` site — powered by
  `lynx_investor_core.urlsafe`.
- Sector-specific ASCII art in easter-egg visuals (replaces the shared
  pickaxe motif that leaked into non-mining sectors).

### Changed
- Aligned every user-visible sector string with the package's real
  sector: titles, subtitles, app class names, splash taglines, news
  keywords, User-Agent headers, themes, export headers, and fortune
  quotes no longer carry template leftovers.
- Depends on `lynx-investor-core>=4.0`.

All notable changes to Lynx Utilities Analysis are documented here.

## [3.0] - 2026-04-22

Part of **Lince Investor Suite v3.0** coordinated release.

### Added
- Uniform PageUp / PageDown navigation across every UI mode (GUI, TUI,
  interactive, console). Scrolling never goes above the current output
  in interactive and console mode; Shift+PageUp / Shift+PageDown remain
  reserved for the terminal emulator's own scrollback.
- Sector-mismatch warning now appends a `Suggestion: use
  'lynx-investor-<other>' instead.` line sourced from
  `lynx_investor_core.sector_registry`. The original warning text is
  preserved as-is.

### Changed
- TUI wires `lynx_investor_core.pager.PagingAppMixin` and
  `tui_paging_bindings()` into the main application.
- Graphical mode binds `<Prior>` / `<Next>` / `<Control-Home>` /
  `<Control-End>` via `bind_tk_paging()`.
- Interactive mode pages long output through `console_pager()` /
  `paged_print()`.
- Depends on `lynx-investor-core>=2.0`.

## [2.0] - 2026-04-22

Initial release of **Lynx Utilities Analysis**, part of the **Lince Investor
Suite v2.0**.

### Added
- **Fundamental analysis engine** specialized for the utilities sector:
  - Regulated Electric utilities (investor-owned, integrated)
  - Regulated Gas utilities (LDCs)
  - Water & wastewater utilities
  - Multi-utilities (combined electric / gas / water)
  - Renewable power utilities and YieldCos
  - Independent Power Producers (IPPs) and merchant generators
  - Nuclear generation operators
  - Transmission & Distribution specialists
  - Diversified utility holding companies
- **Stage-aware analysis**:
  - Early-Stage Developer (greenfield renewable / early-stage)
  - Development-Stage Utility (permitted / financed projects)
  - Pre-Operational / Construction (near-COD projects)
  - Operating Utility (mature regulated / merchant)
  - YieldCo / Holding
- **Utilities-specific metrics**:
  - P/B as a rate-base proxy for regulated names
  - EV/EBITDA, dividend yield and coverage, FCF yield
  - Debt/EBITDA, interest coverage, debt service coverage (FFO proxy)
  - Capex/Revenue, Capex/OCF, reinvestment rate, share-dilution cadence
  - Shareholder yield, FCF / OCF per share, FCF conversion
- **4-level relevance system** (Critical / Important / Relevant / Contextual /
  Irrelevant) with stage overrides that take precedence over tier lookups,
  driving visual highlighting across all interface modes.
- **Utilities Quality Score** (0-100 composite) covering regulatory
  jurisdiction, financial position, dilution risk, asset backing, and
  revenue predictability.
- **Utilities screening checklist** (10 points) covering dividend coverage,
  capital discipline, leverage, jurisdiction, share-structure health.
- **Service-type detection** (Regulated Electric, Regulated Gas, Multi-Utility,
  Water, Renewable Power, Merchant / IPP, Nuclear Generation, T&D,
  Diversified).
- **Regulatory jurisdiction classification**:
  - Tier 1: historically constructive regulators (many US states, UK, Norway,
    Germany, Netherlands, Canada, Australia, New Zealand)
  - Tier 2: mixed / balanced (CA, NY, NJ, IL, OH, MA, CT, MI, PA, Spain,
    Portugal, Italy, France, Japan, Korea, Chile, Mexico, Brazil)
  - Tier 3: All others (challenging regulation)
- **Sector validation gate**: Analysis blocked for non-utility companies
  (oil & gas, mining, tech, finance, healthcare, etc.) with prominent
  warning and suggested sister-agent (lynx-energy, lynx-fundamental).
- **4 interface modes**:
  - Console CLI with progressive output
  - Interactive REPL with command-driven analysis
  - Textual TUI with themes and navigation (utilities-dark / utilities-light)
  - Tkinter GUI
- **Export formats**: TXT, HTML, PDF reports with utility-specific labels
  (Service Type, Rate Base / Asset Quality, Asset Useful Life).
- **Market Intelligence section**:
  - Front-of-curve input benchmarks (Henry Hub natural gas for IPPs /
    gas LDCs; 10Y Treasury yield for rate-sensitive regulated names)
  - Sector ETF tracking (XLU, VPU, PHO, CGW, ICLN, TAN, GRID, URNM)
  - Analyst consensus, short interest, price technicals
  - Insider transaction tracking with buy/sell signals
  - Projected dilution analysis for pre-operational developers
  - Utilities investment disclaimers (interest-rate sensitivity, regulatory
    lag, rate-case outcomes)
- **Intrinsic value estimates** adapted by stage:
  - Operating utilities: DDM / DCF & P/Rate Base
  - Pre-operational: P/NAV of contracted pipeline & asset-based
  - Development stage: EV / Pipeline GW
  - Early-stage: cash backing + pipeline NPV
  - YieldCo / Holding: DDM / CAFD multiple
- **Sector & industry insights** for seven utilities sub-industries
  (Regulated Electric, Regulated Gas, Multi-Utilities, Renewable Electricity,
  IPPs, Regulated Water, Diversified).
- **Comprehensive test suite**: pytest unit tests + Robot Framework
  acceptance tests.
- **Full documentation**: README, DEVELOPMENT guide, API reference.
- **Data caching**: Production (persistent) and testing (always fresh) modes.
- **SEC / international filing download** with rate limiting.
- **News aggregation** from yfinance + Google News RSS ("utilities stock").
- **Easter eggs**: ASCII art, animations, and utility-themed fortune quotes.

### Derived
- Forked from the shared **lynx-investor-energy** base so the UX, keybindings,
  layout, export styling, and overall structure match the rest of the Lince
  Investor suite; only the sector-specialized logic (metrics, insights,
  thresholds, narratives, disclaimers) has been re-authored for utilities.
