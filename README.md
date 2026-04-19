# Lynx Energy Analysis

> Fundamental analysis specialized for oil & gas, uranium, coal & energy companies.

Part of the **Lince Investor Suite**.

## Overview

Lynx Energy is a comprehensive fundamental analysis tool built specifically for energy sector investors. It evaluates companies across all development stages — from early-stage explorers to major producers — using energy-specific metrics, valuation methods, and risk assessments.

### Key Features

- **Stage-Aware Analysis**: Automatically classifies companies as Grassroots Explorer, Advanced Explorer, Developer, Producer, or Royalty/Streaming — and adapts all metrics and scoring accordingly
- **Energy-Specific Metrics**: Cash-to-market-cap ratio, share dilution tracking, cash runway, burn rate analysis, share structure assessment
- **4-Level Relevance System**: Marks each metric as Critical, Relevant, Contextual, or Irrelevant based on the company's development stage
- **Market Intelligence**: Insider transactions, institutional holders, analyst consensus, short interest analysis, price technicals with golden/death cross detection
- **10-Point Energy Screening Checklist**: Evaluates cash runway, dilution, insider ownership, share structure, debt, jurisdiction, and more
- **Jurisdiction Risk Classification**: Tier 1/2/3 based on Fraser Institute methodology
- **Commodity Detection**: Automatic identification of primary commodity (Oil, Natural Gas, Uranium, Coal, etc.)
- **Multiple Interface Modes**: Console CLI, Interactive REPL, Textual TUI, Tkinter GUI
- **Export**: TXT, HTML, and PDF report generation
- **Sector & Industry Insights**: Deep context for Oil & Gas, Uranium, Coal, Thermal Power, and more

### Target Companies

Designed for analyzing companies like:
- **Oil & Gas**: ExxonMobil (XOM), Cenovus Energy (CVE.TO), Ovintiv (OVV), Canadian Natural Resources (CNQ.TO)
- **Uranium**: Cameco (CCO.TO), Denison Mines (DML.TO), NexGen Energy (NXE.TO), Energy Fuels (UUUU)
- **Coal & Thermal**: Various TSX/NYSE energy producers
- **Integrated Energy**: Major and intermediate producers

## Installation

```bash
# Clone or download
cd lynx-investor-energy

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Requirements
- Python >= 3.10
- yfinance, requests, beautifulsoup4, rich, textual, feedparser, pandas, numpy

## Usage

### Direct Execution
```bash
# Via the runner script
./lynx-investor-energy.py -p XOM

# Via Python
python3 lynx-investor-energy.py -p CVE.TO

# Via pip-installed command
lynx-energy -p CCO.TO
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
# Analyze an oil & gas company
lynx-energy -p XOM

# Force fresh data download
lynx-energy -p CVE.TO --refresh

# Search by company name
lynx-energy -p "Cenovus Energy"

# Interactive mode
lynx-energy -p -i

# Export HTML report
lynx-energy -p OVV --export html

# Explain a metric
lynx-energy --explain cash_to_market_cap

# Skip filings and news for faster analysis
lynx-energy -t CCO.TO --no-reports --no-news
```

## Analysis Sections

1. **Company Profile** — Tier, stage, commodity, jurisdiction classification
2. **Sector & Industry Insights** — Energy-specific context and benchmarks
3. **Valuation Metrics** — Traditional + energy-specific (Cash/Market Cap, P/B, EV/EBITDA)
4. **Profitability Metrics** — ROE, ROIC, margins (hidden for pre-revenue stages with explanation)
5. **Solvency & Survival** — Cash runway, burn rate, working capital, NCAV
6. **Growth & Dilution** — Share dilution tracking, 3Y dilution CAGR
7. **Share Structure** — Outstanding/diluted shares, insider/institutional ownership
8. **Energy Quality** — Insider alignment, financial position, dilution risk, asset backing
9. **Intrinsic Value** — DCF, Graham Number, NCAV, Asset-Based (method selection by stage)
10. **Market Intelligence** — Analysts, short interest, technicals, insider trades, risk warnings
11. **Financial Statements** — 5-year annual summary
12. **SEC/SEDAR Filings** — Downloadable regulatory filings
13. **News** — Yahoo Finance + Google News RSS
14. **Assessment Conclusion** — Weighted score, verdict, strengths/risks, screening checklist
15. **Energy Disclaimers** — Stage-specific risk disclosures

## Relevance System

Each metric is classified by importance for the company's development stage:

| Level | Display | Meaning |
|-------|---------|---------|
| **Critical** | `*` bold cyan star | Must-check for this stage |
| **Relevant** | Normal | Important context |
| **Contextual** | Dimmed | Informational only |
| **Irrelevant** | Hidden | Not meaningful for this stage |

Example: For a Grassroots Explorer, Cash Runway is **Critical** while P/E is **Irrelevant**.

## Scoring Methodology

The overall score (0-100) is a weighted average of 5 categories, with weights adapted by both company tier AND development stage:

| Stage | Valuation | Profitability | Solvency | Growth | Energy Quality |
|-------|-----------|---------------|----------|--------|----------------|
| Grassroots | 5% | 5% | 40% | 15% | 35% |
| Explorer | 10% | 5% | 35% | 15% | 35% |
| Developer | 10% | 10% | 35% | 15% | 30% |
| Producer | 20% | 20% | 20% | 20% | 20% |
| Royalty | 25% | 25% | 15% | 15% | 20% |

Verdicts: Strong Buy (>=75), Buy (>=60), Hold (>=45), Caution (>=30), Avoid (<30).

## Project Structure

```
lynx-investor-energy/
├── lynx-investor-energy.py            # Runner script
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
└── lynx_energy/                       # Main package (29 files, ~10,000 LOC)
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
