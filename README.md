# Lynx Utilities Analysis

> Fundamental analysis specialized for regulated electric, gas, water, multi-utilities, independent power producers, and YieldCos.

Part of the **Lince Investor Suite**.

## Overview

Lynx Utilities is a comprehensive fundamental analysis tool built specifically for utilities sector investors. It evaluates companies across all development stages — from early-stage renewable developers to mature regulated operators and YieldCos — using utility-specific metrics, valuation methods, and regulatory-jurisdiction risk assessments.

### Key Features

- **Stage-Aware Analysis**: Automatically classifies companies as Early-Stage Developer, Development-Stage Utility, Pre-Operational / Construction, Operating Utility, or YieldCo / Holding — and adapts all metrics and scoring accordingly
- **Utilities-Specific Metrics**: Rate-base proxy (P/B), allowed-vs-earned ROE context, FFO/Debt & FFO interest coverage proxies, dividend coverage, capex intensity, equity-issuance tracking
- **4-Level Relevance System**: Marks each metric as Critical, Relevant, Contextual, or Irrelevant based on the utility's operating stage
- **Market Intelligence**: Insider transactions, institutional holders, analyst consensus, short interest, price technicals with golden/death cross detection, and sector-ETF (XLU / VPU) context
- **10-Point Utilities Screening Checklist**: Evaluates dividend coverage, capital discipline, leverage, regulatory jurisdiction, share-structure health, and more
- **Regulatory Jurisdiction Classification**: Tier 1/2/3 buckets reflecting historically constructive vs challenging regulators
- **Service-Type Detection**: Automatic identification of primary utility service (Regulated Electric, Regulated Gas, Water, Multi-Utility, Merchant / IPP, Renewable Power, Nuclear, T&D, Diversified)
- **Multiple Interface Modes**: Console CLI, Interactive REPL, Textual TUI, Tkinter GUI
- **Export**: TXT, HTML, and PDF report generation
- **Sector & Industry Insights**: Deep context for Regulated Electric, Regulated Gas, Multi-Utilities, Renewable Electricity, IPPs, Water, and Diversified Utilities

### Target Companies

Designed for analyzing companies like:
- **Regulated Electric**: NextEra Energy (NEE), Duke Energy (DUK), Southern Company (SO), American Electric Power (AEP), Xcel Energy (XEL)
- **Regulated Gas (LDCs)**: Atmos Energy (ATO), NiSource (NI), Southwest Gas (SWX)
- **Water**: American Water Works (AWK), Essential Utilities (WTRG), American States Water (AWR)
- **IPPs / Merchant**: NRG Energy (NRG), Vistra (VST), Constellation Energy (CEG)
- **YieldCo / Renewable**: Brookfield Renewable (BEP), Clearway Energy (CWEN), NextEra Energy Partners (NEP)
- **European Utilities**: Iberdrola (IBE.MC), Enel (ENEL.MI), National Grid (NG.L), EDF (EDF.PA)

## Installation

```bash
# Clone the repository
git clone https://github.com/borjatarraso/lynx-investor-utilities.git
cd lynx-investor-utilities

# Install in editable mode (creates the `lynx-utilities` command)
pip install -e .
```

### Dependencies

| Package        | Purpose                              |
|----------------|--------------------------------------|
| yfinance       | Financial data from Yahoo Finance    |
| requests       | HTTP calls (OpenFIGI, EDGAR, etc.)   |
| beautifulsoup4 | HTML parsing for SEC filings         |
| rich           | Terminal tables and formatting       |
| textual        | Full-screen TUI framework            |
| feedparser     | News RSS feed parsing                |
| pandas         | Data analysis                        |
| numpy          | Numerical computing                  |

All dependencies are installed automatically via `pip install -e .`.

## Usage

### Direct Execution
```bash
# Via the runner script
./lynx-investor-utilities.py -p NEE

# Via Python
python3 lynx-investor-utilities.py -p DUK

# Via pip-installed command
lynx-utilities -p AWK
```

### Execution Modes

| Flag | Mode | Description |
|------|------|-------------|
| `-p` | Production | Uses `data/` for persistent cache |
| `-t` | Testing | Uses `data_test/` (isolated, always fresh) |

### Interface Modes

| Flag | Interface | Description |
|------|-----------|-------------|
| (none) | Console | Progressive CLI output |
| `-i` | Interactive | REPL with commands |
| `-tui` | TUI | Textual terminal UI with themes |
| `-x` | GUI | Tkinter graphical interface |

### Examples

```bash
# Analyze a regulated electric utility
lynx-utilities -p NEE

# Force fresh data download
lynx-utilities -p DUK --refresh

# Search by company name
lynx-utilities -p "NextEra Energy"

# Interactive mode
lynx-utilities -p -i

# Export HTML report
lynx-utilities -p SO --export html

# Explain a metric
lynx-utilities --explain dividend_coverage

# Skip filings and news for faster analysis
lynx-utilities -t AWK --no-reports --no-news
```

## Analysis Sections

1. **Company Profile** — Tier, stage, service type, regulatory-jurisdiction classification
2. **Sector & Industry Insights** — Utilities-specific context and benchmarks
3. **Valuation Metrics** — Traditional + utility-specific (P/B as rate-base proxy, EV/EBITDA, dividend yield, FCF yield)
4. **Profitability Metrics** — ROE vs allowed ROE, ROIC, EBITDA margin (hidden for pre-operational stages with explanation)
5. **Solvency & Credit** — Interest coverage, debt/EBITDA, FFO proxies, working capital
6. **Growth & Capital Allocation** — EPS growth, rate-base growth proxies, equity-issuance cadence, dividend coverage
7. **Share Structure** — Outstanding/diluted shares, insider/institutional ownership
8. **Utilities Quality** — Regulatory jurisdiction, financial position, dilution risk, asset backing
9. **Intrinsic Value** — DDM / DCF, P/Rate Base, Asset-Based (method selection by stage)
10. **Market Intelligence** — Analysts, short interest, technicals, insider trades, sector-ETF context, risk warnings
11. **Financial Statements** — 5-year annual summary
12. **SEC/SEDAR Filings** — Downloadable regulatory filings
13. **News** — Yahoo Finance + Google News RSS
14. **Assessment Conclusion** — Weighted score, verdict, strengths/risks, screening checklist
15. **Utilities Disclaimers** — Stage-specific risk disclosures (interest-rate sensitivity, regulatory lag, rate-case outcomes)

## Relevance System

Each metric is classified by importance for the company's operating stage:

| Level | Display | Meaning |
|-------|---------|---------|
| **Critical** | `*` bold cyan star | Must-check for this stage |
| **Important** | Highlighted | Drives the verdict |
| **Relevant** | Normal | Important context |
| **Contextual** | Dimmed | Informational only |
| **Irrelevant** | Hidden | Not meaningful for this stage |

Example: For an Early-Stage Developer, Cash Runway is **Critical** while P/E is **Irrelevant**. For an Operating Utility, Dividend Coverage and EV/EBITDA are **Critical** while Cash Runway becomes **Contextual**.

## Scoring Methodology

The overall score (0-100) is a weighted average of 5 categories, with weights adapted by both company tier AND development stage:

| Stage | Valuation | Profitability | Solvency | Growth | Utility Quality |
|-------|-----------|---------------|----------|--------|-----------------|
| Early-Stage Developer | 5% | 5% | 40% | 15% | 35% |
| Development-Stage Utility | 10% | 5% | 35% | 15% | 35% |
| Pre-Operational | 10% | 10% | 35% | 15% | 30% |
| Operating Utility | 20% | 25% | 20% | 15% | 20% |
| YieldCo / Holding | 25% | 25% | 15% | 15% | 20% |

Verdicts: Strong Buy (>=75), Buy (>=60), Hold (>=45), Caution (>=30), Avoid (<30).

## Project Structure

```
lynx-investor-utilities/
├── lynx-investor-utilities.py         # Runner script
├── pyproject.toml                     # Build configuration
├── requirements.txt                   # Dependencies
├── img/                               # Logo images
├── data/                              # Production cache
├── data_test/                         # Testing cache
├── docs/                              # Documentation
│   └── API.md                         # API reference
├── robot/                             # Robot Framework tests
│   ├── cli_tests.robot
│   ├── api_tests.robot
│   └── export_tests.robot
├── tests/                             # Unit tests
└── lynx_utilities/                    # Main package (29 files, ~10,000 LOC)
```

## Testing

```bash
# Unit tests
pytest tests/ -v

# Robot Framework acceptance tests
robot robot/
```

## License

BSD 3-Clause License. See LICENSE in source.

## Author

**Borja Tarraso** — borja.tarraso@member.fsf.org
