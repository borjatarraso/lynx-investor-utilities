# Changelog

All notable changes to Lynx Energy Analysis are documented here.

## [0.2] - 2026-04-19

### Fixed
- **(CRITICAL) Sector validation too loose**: Generic words like "production", "gas", "thermal" in company descriptions caused non-energy companies (e.g. Apple, Microsoft) to pass the sector gate. Regex patterns now require energy-specific phrases ("crude oil", "oil production", "natural gas", "thermal coal") instead of bare generic words
- **(CRITICAL) Integrated oil majors misclassified as Royalty/Streaming**: The keyword "stream" matched "downstream" in descriptions of integrated majors like Exxon Mobil. Removed bare "stream" from royalty detection; now requires exact "streaming" or "royalty" via word-boundary regex
- **(HIGH) Pre-revenue stage check in exports used wrong enum value**: Exports checked for "Grassroots Explorer" but the actual enum value is "Early Exploration", causing pre-revenue profitability messages to not appear in TXT/HTML exports
- **(HIGH) Short % of Float double-scaled in exports**: `short_pct_of_float` was stored as percentage (5.0) instead of ratio (0.05), then exports called `_fmt_pct()` which multiplied by 100 again, displaying 500% instead of 5%. Now stored as ratio consistently with all other percentage fields
- **(MEDIUM) Extreme dilution penalty unreachable**: `elif dil > 0.20` was checked after `elif dil > 0.10`, making the -25 point penalty for >20% dilution unreachable. Reversed the order so extreme dilution gets the full penalty
- **(MEDIUM) Revenue-generating companies with no stage keywords had no default**: Companies with $10M+ revenue but no specific producer/royalty keywords in their description fell through to the general keyword loop. Now defaults to Producer when revenue threshold is met
- **(LOW) 52-week low display showed `+-X.X%`**: Hardcoded `+` prefix before percentage caused double sign when price was below 52-week low. Now uses `:+.1f` format specifier
- **(LOW) Jurisdiction substring matching false positives**: "india" in description matched "Indiana" (US state), classifying US companies as Tier 2. Now uses word-boundary regex for description matching; country field still uses substring (reliable)
- **(LOW) Redundant `U3O8` keyword**: Uppercase "U3O8" in commodity keywords never matched since search text is lowercased. Removed the dead entry
- **(LOW) Orphaned screening labels in display**: 4 screening checklist labels (`positive_fcf`, `book_value_growing`, `reasonable_valuation`, `institutional_interest`) were defined but never produced by the scoring engine. Removed dead labels

### Changed
- **TUI theme renamed**: "mining-dark" / "mining-light" → "energy-dark" / "energy-light"
- **GUI icon updated**: Pickaxe icon for quality section replaced with lightning bolt
- Version bumped to 0.2

### Added
- **8 new tests** for sector validation (generic production blocked, generic gas blocked, standalone downstream blocked, crude oil in desc allowed, uranium in desc allowed)
- **2 new tests** for stage classification (integrated major not classified as royalty, revenue defaults to producer)
- **1 new test** for dilution scoring (extreme dilution gets full penalty)
- Total: 161 tests, all passing

## [0.1] - 2026-04-19

### Added
- Initial release of Lynx Energy Analysis
- **Fundamental analysis engine** specialized for the energy sector:
  - Oil & Gas E&P, Integrated, Midstream, Refining & Marketing, Equipment & Services
  - Uranium producers and explorers
  - Thermal coal companies
  - Solar and renewable energy companies
- **Stage-aware analysis** (Early Exploration / Advanced Explorer / Developer / Producer / Royalty)
- **Energy-specific metrics**:
  - EV/BOE and EV/MCFE for reserve valuation
  - Netback per BOE and operating cost analysis
  - Cash-to-market-cap, share dilution tracking, cash runway, burn rate
  - Share structure assessment and dilution risk scoring
- **4-level relevance system** (Critical / Relevant / Contextual / Irrelevant)
  - Stage overrides take precedence over tier-based lookups
  - Drives visual highlighting across all interface modes
- **Energy Quality Score** (0-100 composite):
  - Insider alignment (20 pts), Financial position (25 pts), Dilution risk (20 pts)
  - Asset backing (20 pts), Revenue/stage status (15 pts)
- **Energy screening checklist** evaluating key quality criteria
- **Commodity detection** (Crude Oil, Natural Gas, LNG, NGL, Uranium, Coal, Hydrogen, Renewable)
- **Jurisdiction risk classification** adapted for energy-producing nations
  - Tier 1: Canada (Alberta, BC, SK), US (TX, ND, OK, CO, LA, PA), Australia, Norway, UK
  - Tier 2: Mexico, Brazil, Colombia, Argentina, Guyana, Malaysia, Indonesia, Kazakhstan
  - Tier 3: All others
- **Sector validation gate**: Analysis blocked for non-energy companies with prominent warning
- **4 interface modes**:
  - Console CLI with progressive output
  - Interactive REPL with command-driven analysis
  - Textual TUI with themes and navigation
  - Tkinter GUI with Catppuccin Mocha dark theme
- **Export formats**: TXT, HTML, PDF reports
- **Market Intelligence section**:
  - Commodity market context (WTI, Natural Gas, Uranium spot prices via yfinance)
  - Sector ETF tracking (XLE, XOP, FCG, URA, URNM, KOL, ICLN, TAN)
  - Analyst consensus, short interest, price technicals
  - Insider transaction tracking with buy/sell signals
  - Projected dilution analysis for pre-revenue companies
  - Energy investment disclaimers (stage-specific)
- **Intrinsic value estimates** adapted by stage:
  - Producers: DCF / EV/EBITDA comps
  - Developers: P/NAV from field development economics
  - Explorers: EV/BOE and asset-based
  - Early exploration: Cash backing
  - Royalty: DCF / P/NAV
- **Sector & industry insights** for 8 energy sub-industries
- **Comprehensive test suite**: 153 unit tests + Robot Framework acceptance tests
- **Full documentation**: README, DEVELOPMENT guide, API reference
- **Data caching**: Production (persistent) and testing (always fresh) modes
- **SEC/SEDAR filing download** with rate limiting
- **News aggregation** from yfinance + Google News RSS
- **Easter eggs**: ASCII art, animations, fortune quotes
