# Development Guide

## Architecture

The application follows the same architecture as `lynx-fundamental` with utilities-specific adaptations.

### Data Flow

```
User Input (ticker/ISIN/name)
    ↓
CLI/Interactive/TUI/GUI → cli.py
    ↓
analyzer.py: run_progressive_analysis()
    ↓
ticker.py: resolve_identifier() → (ticker, isin)
    ↓
storage.py: check cache → return if cached
    ↓
fetcher.py: yfinance data (profile + financials)
    ↓
models.py: classify_stage/commodity/jurisdiction
    ↓
calculator.py: calc_valuation/profitability/solvency/growth/...
    ↓
calculator.py: calc_share_structure + calc_energy_quality
    ↓
calculator.py: calc_market_intelligence (insider, analyst, short, technicals)
    ↓
calculator.py: calc_intrinsic_value
    ↓
[parallel] reports.py + news.py
    ↓
conclusion.py: generate_conclusion() → verdict + screening
    ↓
storage.py: save_analysis_report()
    ↓
display.py / tui/app.py / gui/app.py → render
```

### Key Design Decisions

1. **Stage > Tier**: Utility operating stage (regulated operator vs merchant
   generator vs pre-operational developer vs YieldCo) is the primary analysis
   axis, not market-cap tier. The relevance system prioritizes stage overrides.

2. **Relevance-Driven Display**: All 4 UI modes use `get_relevance()` to
   determine which metrics to highlight, dim, or hide. This keeps the display
   focused on what matters.

3. **Progressive Rendering**: The analyzer emits progress callbacks so UIs can
   render sections as data arrives, rather than waiting for the full pipeline.

4. **Rich Tables in TUI**: Sections with long text use Rich `Table` objects
   rendered via `Static` widgets (not Textual `DataTable`) because Rich tables
   support multi-line cell wrapping.

5. **Utilities Disclaimers**: Every analysis includes stage-specific risk
   disclosures — interest-rate sensitivity, rate-case outcomes, and
   construction cost-overrun risk — to ensure responsible use.

6. **Schema parity with the rest of the suite**: The dataclass
   `EnergyQualityIndicators` and the dict key `energy_quality` are preserved
   verbatim across all sister agents (lynx-energy, lynx-basic-materials,
   lynx-information-technology, lynx-utilities, ...) so the shared core and
   export/report tooling can operate generically. The *contents* of those
   fields carry utility-specific text here.

### Adding New Metrics

1. Add field to the appropriate dataclass in `models.py`
2. Calculate in `calculator.py` (in the relevant `calc_*` function)
3. Add relevance entry in `relevance.py` (_STAGE_OVERRIDES and tier tables)
4. Add explanation in `explanations.py`
5. Add display row in `display.py`, `tui/app.py`, `gui/app.py`

### Adding New Service Types

1. Add to `Commodity` enum in `models.py` (name kept for cross-suite parity;
   the values describe utility service types)
2. Add keywords to `_COMMODITY_KEYWORDS`
3. Add sector-ETF and benchmark proxy entries in `calculator.py`
4. Add industry insight in `sector_insights.py`

### Adding New Stages

1. Add to `CompanyStage` enum
2. Add keywords to `_STAGE_KEYWORDS`
3. Add weights to `_WEIGHTS` in `conclusion.py`
4. Add relevance overrides in `relevance.py`

## Running Tests

```bash
# Python unit tests
pytest tests/ -v --tb=short

# Robot Framework (requires robotframework)
pip install robotframework
robot --outputdir results robot/

# Syntax check all files
python -c "import py_compile, glob; [py_compile.compile(f, doraise=True) for f in glob.glob('lynx_utilities/**/*.py', recursive=True)]"
```

## Code Style

- Python 3.10+ with type hints
- Dataclasses for all data models
- Rich for console rendering
- Textual for TUI
- Tkinter for GUI (Catppuccin Mocha theme)
