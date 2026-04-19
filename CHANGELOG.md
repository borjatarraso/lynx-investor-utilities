# Changelog

All notable changes to Lynx Energy Analysis are documented here.

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
