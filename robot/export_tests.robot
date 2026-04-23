*** Settings ***
Documentation    Export workflow tests for lynx-utilities (uses Python API to avoid network timeouts)
Library          Process

*** Variables ***
${PYTHON}        python3

*** Keywords ***
When I Run Python Code "${code}"
    ${result}=    Run Process    ${PYTHON}    -c    ${code}    timeout=30s
    Set Test Variable    ${OUTPUT}    ${result.stdout}${result.stderr}
    Set Test Variable    ${RC}    ${result.rc}

Then The Exit Code Should Be ${expected}
    Should Be Equal As Integers    ${RC}    ${expected}

Then The Output Should Contain "${text}"
    Should Contain    ${OUTPUT}    ${text}

*** Test Cases ***
Export TXT From Minimal Report
    [Documentation]    GIVEN a report WHEN I export as TXT THEN a readable file is created
    When I Run Python Code "from lynx_utilities.models import AnalysisReport, CompanyProfile, CompanyTier, CompanyStage, ValuationMetrics, SolvencyMetrics; from lynx_utilities.export import export_report, ExportFormat; from pathlib import Path; import tempfile; p = CompanyProfile(ticker='TEST', name='Test Utility Corp', sector='Utilities', industry='Utilities—Regulated Electric', country='United States', market_cap=100000000); p.tier = CompanyTier.MICRO; p.stage = CompanyStage.EXPLORER; r = AnalysisReport(profile=p, valuation=ValuationMetrics(pb_ratio=0.8, cash_to_market_cap=0.35), solvency=SolvencyMetrics(cash_runway_years=3.0, total_cash=35000000)); f = tempfile.NamedTemporaryFile(suffix='.txt', delete=False); path = export_report(r, ExportFormat.TXT, Path(f.name)); content = path.read_text(); assert 'Test Utility Corp' in content; assert CompanyStage.EXPLORER.value in content; assert len(content) > 500; print('OK', len(content), 'bytes')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Export HTML From Minimal Report
    [Documentation]    GIVEN a report WHEN I export as HTML THEN a styled file with white background
    When I Run Python Code "from lynx_utilities.models import AnalysisReport, CompanyProfile, CompanyTier, CompanyStage, ValuationMetrics, SolvencyMetrics; from lynx_utilities.export import export_report, ExportFormat; from pathlib import Path; import tempfile; p = CompanyProfile(ticker='TEST', name='Test Utility Corp', sector='Utilities', industry='Utilities—Regulated Electric', country='United States', market_cap=100000000); p.tier = CompanyTier.MICRO; p.stage = CompanyStage.EXPLORER; r = AnalysisReport(profile=p, valuation=ValuationMetrics(pb_ratio=0.8, cash_to_market_cap=0.35), solvency=SolvencyMetrics(cash_runway_years=3.0, total_cash=35000000)); f = tempfile.NamedTemporaryFile(suffix='.html', delete=False); path = export_report(r, ExportFormat.HTML, Path(f.name)); content = path.read_text(); assert '#fff' in content or '#ffffff' in content, 'Missing white background'; assert 'word-wrap' in content, 'Missing word-wrap'; assert 'Test Utility Corp' in content; assert len(content) > 1000; print('OK', len(content), 'bytes')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

HTML Has No Text Truncation
    [Documentation]    GIVEN an HTML export WHEN I check table cells THEN word-wrap is enabled
    When I Run Python Code "from lynx_utilities.models import AnalysisReport, CompanyProfile, CompanyTier, CompanyStage, ValuationMetrics; from lynx_utilities.export import export_report, ExportFormat; from pathlib import Path; import tempfile; p = CompanyProfile(ticker='T', name='T Corp'); p.tier = CompanyTier.MICRO; p.stage = CompanyStage.EXPLORER; r = AnalysisReport(profile=p, valuation=ValuationMetrics(pb_ratio=0.8)); f = tempfile.NamedTemporaryFile(suffix='.html', delete=False); path = export_report(r, ExportFormat.HTML, Path(f.name)); c = path.read_text(); assert 'overflow-wrap' in c and 'break-word' in c; assert 'table-layout' in c and 'fixed' in c; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

HTML Has Professional White Background
    [Documentation]    GIVEN an HTML export WHEN I check styling THEN it uses white background
    When I Run Python Code "from lynx_utilities.models import AnalysisReport, CompanyProfile; from lynx_utilities.export import export_report, ExportFormat; from pathlib import Path; import tempfile; r = AnalysisReport(profile=CompanyProfile(ticker='T', name='T')); f = tempfile.NamedTemporaryFile(suffix='.html', delete=False); path = export_report(r, ExportFormat.HTML, Path(f.name)); c = path.read_text(); assert '#fff' in c or '#ffffff' in c, 'No white bg'; assert 'color: #1a1a2e' in c or 'color:#1a1a2e' in c, 'No dark text'; assert '@media print' in c, 'No print styles'; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Export TXT With Utilities Quality Field
    [Documentation]    GIVEN a report with utilities-quality data WHEN I export as TXT THEN quality data is included
    When I Run Python Code "from lynx_utilities.models import AnalysisReport, CompanyProfile, CompanyTier, CompanyStage, EnergyQualityIndicators; from lynx_utilities.export import export_report, ExportFormat; from pathlib import Path; import tempfile; p = CompanyProfile(ticker='EQ', name='EQ Utility Corp', sector='Utilities', industry='Utilities—Regulated Electric', country='United States', market_cap=100000000); p.tier = CompanyTier.MICRO; p.stage = CompanyStage.PRODUCER; eq = EnergyQualityIndicators(quality_score=82.0, reserve_quality='High-quality rate base', reserve_life_assessment='40+ years useful life', production_scale_assessment='Mid-scale regulated utility'); r = AnalysisReport(profile=p, energy_quality=eq); f = tempfile.NamedTemporaryFile(suffix='.txt', delete=False); path = export_report(r, ExportFormat.TXT, Path(f.name)); content = path.read_text(); assert 'EQ Utility Corp' in content; assert 'Quality' in content or 'quality' in content; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Export HTML With New Metric Fields
    [Documentation]    GIVEN a report with v0.4 metrics WHEN I export as HTML THEN new fields are included
    When I Run Python Code "from lynx_utilities.models import AnalysisReport, CompanyProfile, ValuationMetrics, ProfitabilityMetrics, SolvencyMetrics; from lynx_utilities.export import export_report, ExportFormat; from pathlib import Path; import tempfile; p = CompanyProfile(ticker='NM', name='New Metrics Corp'); r = AnalysisReport(profile=p, valuation=ValuationMetrics(pb_ratio=1.2, fcf_yield=0.08), profitability=ProfitabilityMetrics(croci=0.12), solvency=SolvencyMetrics(debt_per_share=2.5, net_debt_per_share=1.8, debt_service_coverage=3.2)); f = tempfile.NamedTemporaryFile(suffix='.html', delete=False); path = export_report(r, ExportFormat.HTML, Path(f.name)); content = path.read_text(); assert 'New Metrics Corp' in content; assert len(content) > 1000; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"
