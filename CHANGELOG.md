# Changelog

All notable changes to Lynx Energy Analysis are documented here.

## [0.5] - 2026-04-19

### Fixed (30+ bugs from deep audit)

**Critical / High:**
- **Profitability table crash**: Pre-revenue companies (Explorer/Grassroots) caused a Rich `MissingColumn` crash — table had 4 columns but the N/A row only passed 3 values
- **FCF yield only calculated for positive FCF**: Negative FCF (cash burn) was silently dropped, preventing scoring of cash-burning companies. Now negative yields are calculated and scored
- **Altman Z-Score explosion**: When `total_liabilities` was 0, the formula defaulted to dividing by 1, producing astronomical Z-scores. Now skips Z-Score when liabilities data is missing
- **Negative D/E rewarded as strength**: A negative debt-to-equity ratio (meaning negative equity/insolvency) was given +15 bonus points. Now only zero debt gets the bonus; negative D/E gets no reward
- **Conservative balance sheet false positive**: Companies with negative equity (D/E < 0) were listed as a "strength". Now requires `0 <= D/E < 0.2`
- **News RSS search used "mining stock"**: Google News queries returned irrelevant mining results for energy companies. Changed to "energy stock"
- **EDGAR User-Agent said "LynxMining"**: SEC EDGAR requests used wrong product identifier, risking request blocks

**Medium:**
- **OCF/Net Income ratio distorted**: `abs()` on denominator made loss-making companies appear to have high earnings quality. Now only calculated when net income > 0
- **Burn rate required 2 financial statements**: Companies with only 1 year of data couldn't get burn rate calculated. Removed artificial requirement
- **Projected dilution was 2-year rate labeled as annual**: `projected_dilution_annual_pct` stored total 2-year dilution, not annual. Now divides by 2
- **P/Tangible Book not computed for Mid Cap**: The tier gate excluded MID tier despite relevance system marking it as RELEVANT. Added MID to computation scope
- **Ticker error message suggested mining tickers**: OCO.V, FUU.V, UUUU examples replaced with energy tickers (XOM, OVV, CVE.TO)
- **9 GUI metric keys empty**: Solvency, growth, and share structure rows bypassed relevance filtering. All keys populated
- **GUI share structure info buttons disabled**: `metric_key=""` hardcoded; changed to pass actual key
- **GUI thread safety**: tkinter BooleanVars read from background thread; now read on main thread before spawning worker
- **GUI macOS mouse wheel**: `e.delta // 120` produced 0 on macOS; now platform-detected
- **Duplicate except clause in interactive mode**: Unreachable `except Exception` dead code removed

**Low (truthiness bugs — 0.0 treated as "no data"):**
- `cash_runway_years = 0.0` showed "N/A" instead of "0.0 years" (hid critical data)
- `cash_per_share = 0.0` showed "N/A" instead of "$0.00"
- `insider_ownership_pct = 0.0` showed "N/A" instead of "0.00%"
- `institutional_ownership_pct = 0.0` showed "N/A"
- `pct_from_52w_high = 0.0` showed empty string
- `institutions_pct = 0.0` hid the percentage display
- `current_price = 0.0` showed "N/A" in intrinsic value table
- All fixed to use `is not None` checks

### Changed
- Version bumped to 0.5
- Total: 173 tests passing

## [0.4] - 2026-04-19

### Added
- **Impact column** in all metric tables showing relevance level with color coding:
  - Critical (blinking red), Important (orange), Relevant (yellow), Informational (green), Irrelevant (grey/hidden)
- **IMPORTANT relevance level** between CRITICAL and RELEVANT for key metrics (P/E, D/E, ROE, EV/Revenue, share dilution) — displayed with `>` prefix and orange Impact tag
- **Severity markers** updated to final format across all 53 assessment functions:
  - `***CRITICAL***` — bold red uppercase
  - `*WARNING*` — orange text
  - `[WATCH]` — yellow text in brackets
  - `[OK]` — green text in brackets
  - `[STRONG]` — grey/silver text in brackets
- **12 new unit tests**: 7 for new energy metrics (FCF yield, CROCI, OCF/NI, debt/share, capex/revenue, FCF/share, dividend coverage), 5 for IMPORTANT relevance level
- Updated Robot Framework tests for IMPORTANT level and new metrics
- Updated API documentation with all new fields and Impact column behavior

### Fixed
- **Financial statements table** truncation — increased Period column width and enabled table expansion
- **Insider transactions table** — dates trimmed to YYYY-MM-DD, columns use ratio-based widths to prevent truncation
- **Header legend** updated to show `>` = important marker alongside `*` = critical

### Changed
- All 4 UI modes (Console, TUI, GUI, Interactive) handle the IMPORTANT relevance level
- Version bumped to 0.4
- Total: 173 tests passing, 53 metric explanations

## [0.3] - 2026-04-19

### Added
- **15 new energy-specific metrics** across all analysis sections:
  - **Valuation**: FCF Yield (FCF / Enterprise Value) — the primary valuation anchor for energy producers
  - **Profitability**: CROCI (Cash Return on Capital Invested), OCF/Net Income ratio (earnings quality check)
  - **Solvency**: Debt Per Share, Net Debt Per Share, Debt Service Coverage (OCF / interest expense)
  - **Growth & Capital Discipline**: Capex/Revenue, Capex/OCF, Reinvestment Rate (Capex/EBITDA), Dividend Payout Ratio, Dividend Coverage (FCF/Dividends), Shareholder Yield, FCF Per Share, OCF Per Share
  - **Efficiency**: FCF Conversion (FCF/EBITDA), Capex Intensity (Capex/Revenue)
- **Severity markers** on ALL metric assessments — color-coded with distinct formatting:
  - `***CRITICAL***` — urgent red flag, bold red uppercase text
  - `*WARNING*` — significant concern, orange text
  - `[WATCH]` — needs monitoring, yellow text
  - `[OK]` — normal range, green text
  - `[STRONG]` — excellent signal, grey/silver text
- **Impact column** added to all metric tables showing relevance level:
  - Critical — blinking red text
  - Important — orange text
  - Relevant — yellow text
  - Informational — green text
  - Irrelevant — grey text (hidden metrics)
- **New IMPORTANT relevance level** added between CRITICAL and RELEVANT for metrics that are truly important but not quite critical (P/E for producers, D/E ratio, EV/Revenue, ROE, share dilution)
- **15 new assessment functions** with severity-graded thresholds tailored to energy sector benchmarks
- **2 new screening checklist criteria** for energy producers:
  - Capital Discipline (Capex <80% of OCF)
  - Dividend Covered by FCF
- **15 new metric explanations** in the --explain system with energy-specific context
- **Stage-aware relevance overrides** for all 15 new metrics (e.g., FCF Yield is *CRITICAL* for producers, *IRRELEVANT* for explorers)
- **Scoring integration**: FCF Yield, CROCI, Debt Service Coverage, Capex/OCF, and Dividend Coverage now contribute to the composite scoring across valuation, profitability, solvency, and growth categories
- Total explained metrics: 53 (up from 38)

### Changed
- All existing assessment functions (38 total) updated with severity markers between asterisks
- Version bumped to 0.3

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
