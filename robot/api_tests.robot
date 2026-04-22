*** Settings ***
Documentation    Python API tests for lynx-utilities
Library          Process

*** Variables ***
${PYTHON}        python3

*** Keywords ***
When I Run Python Code "${code}"
    ${result}=    Run Process    ${PYTHON}    -c    ${code}    timeout=120s
    Set Test Variable    ${OUTPUT}    ${result.stdout}${result.stderr}
    Set Test Variable    ${RC}    ${result.rc}

Then The Exit Code Should Be ${expected}
    Should Be Equal As Integers    ${RC}    ${expected}

Then The Output Should Contain "${text}"
    Should Contain    ${OUTPUT}    ${text}

*** Test Cases ***
Import All Models
    [Documentation]    GIVEN the package WHEN I import models THEN all classes are available
    When I Run Python Code "from lynx_utilities.models import AnalysisReport, CompanyProfile, CompanyStage, CompanyTier, Commodity, JurisdictionTier, Relevance, MarketIntelligence, InsiderTransaction; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Import All Calculators
    [Documentation]    GIVEN the package WHEN I import calculators THEN all functions exist
    When I Run Python Code "from lynx_utilities.metrics.calculator import calc_valuation, calc_profitability, calc_solvency, calc_growth, calc_efficiency, calc_share_structure, calc_energy_quality, calc_intrinsic_value, calc_market_intelligence; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Classify Company Tier Mega Cap
    [Documentation]    GIVEN a large market cap WHEN I classify THEN it returns Mega Cap
    When I Run Python Code "from lynx_utilities.models import classify_tier; print(classify_tier(500_000_000_000).value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Mega Cap"

Classify Company Tier Micro Cap
    [Documentation]    GIVEN a small market cap WHEN I classify THEN it returns Micro Cap
    When I Run Python Code "from lynx_utilities.models import classify_tier; print(classify_tier(100_000_000).value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Micro Cap"

Classify Company Tier None
    [Documentation]    GIVEN None market cap WHEN I classify THEN it returns Nano Cap
    When I Run Python Code "from lynx_utilities.models import classify_tier; print(classify_tier(None).value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Nano Cap"

Classify Utility Stage Explorer
    [Documentation]    GIVEN a development pipeline description WHEN I classify THEN Development-Stage Utility
    When I Run Python Code "from lynx_utilities.models import classify_stage; print(classify_stage('development pipeline includes 3 GW of permitted projects with PPA signed', 0).value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Development-Stage Utility"

Classify Utility Stage Producer
    [Documentation]    GIVEN an operating utility description WHEN I classify THEN Operating Utility
    When I Run Python Code "from lynx_utilities.models import classify_stage; print(classify_stage('regulated electric utility with rate base and transmission and distribution', 500000000).value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Operating Utility"

Classify Utility Stage Developer
    [Documentation]    GIVEN a project-under-construction description WHEN I classify THEN Pre-Operational
    When I Run Python Code "from lynx_utilities.models import classify_stage; print(classify_stage('wind farm under construction, commercial operation date 2027', 0).value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Pre-Operational"

Classify Utility Stage Grassroots
    [Documentation]    GIVEN early-stage renewable development WHEN I classify THEN Early-Stage Developer
    When I Run Python Code "from lynx_utilities.models import classify_stage; print(classify_stage('early stage development of greenfield solar site, resource assessment', 0).value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Early-Stage Developer"

Classify Commodity Regulated Electric
    [Documentation]    GIVEN regulated electric text WHEN I classify THEN Regulated Electric detected
    When I Run Python Code "from lynx_utilities.models import classify_commodity; print(classify_commodity('regulated electric utility', 'Utilities—Regulated Electric').value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Regulated Electric"

Classify Commodity Regulated Gas
    [Documentation]    GIVEN regulated gas text WHEN I classify THEN Regulated Gas detected
    When I Run Python Code "from lynx_utilities.models import classify_commodity; print(classify_commodity('natural gas utility local distribution company', 'Utilities—Regulated Gas').value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Regulated Gas"

Classify Jurisdiction Tier 1
    [Documentation]    GIVEN Canada WHEN I classify THEN Tier 1
    When I Run Python Code "from lynx_utilities.models import classify_jurisdiction; print(classify_jurisdiction('Canada').value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Tier 1"

Classify Jurisdiction Tier 2
    [Documentation]    GIVEN Mexico WHEN I classify THEN Tier 2
    When I Run Python Code "from lynx_utilities.models import classify_jurisdiction; print(classify_jurisdiction('Mexico').value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Tier 2"

Relevance Enum Includes IMPORTANT
    [Documentation]    GIVEN Relevance enum WHEN I access IMPORTANT THEN it exists between CRITICAL and RELEVANT
    When I Run Python Code "from lynx_utilities.models import Relevance; vals = [r.value for r in Relevance]; assert 'important' in vals; idx_c = vals.index('critical'); idx_i = vals.index('important'); idx_r = vals.index('relevant'); assert idx_c < idx_i < idx_r; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Relevance Explorer PE Irrelevant
    [Documentation]    GIVEN explorer WHEN I check P/E THEN irrelevant
    When I Run Python Code "from lynx_utilities.metrics.relevance import get_relevance; from lynx_utilities.models import CompanyTier, CompanyStage; print(get_relevance('pe_trailing', CompanyTier.MICRO, 'valuation', CompanyStage.EXPLORER).value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "irrelevant"

Relevance Explorer Cash Runway Critical
    [Documentation]    GIVEN explorer WHEN I check cash runway THEN critical
    When I Run Python Code "from lynx_utilities.metrics.relevance import get_relevance; from lynx_utilities.models import CompanyTier, CompanyStage; print(get_relevance('cash_runway_years', CompanyTier.MICRO, 'solvency', CompanyStage.EXPLORER).value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "critical"

Relevance Producer EV EBITDA Critical
    [Documentation]    GIVEN producer WHEN I check EV/EBITDA THEN critical
    When I Run Python Code "from lynx_utilities.metrics.relevance import get_relevance; from lynx_utilities.models import CompanyTier, CompanyStage; print(get_relevance('ev_ebitda', CompanyTier.MID, 'valuation', CompanyStage.PRODUCER).value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "critical"

Get Metric Explanation
    [Documentation]    GIVEN metric key WHEN I get explanation THEN details returned
    When I Run Python Code "from lynx_utilities.metrics.explanations import get_explanation; e = get_explanation('cash_to_market_cap'); print(e.full_name)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Cash-to-Market-Cap"

Get Unknown Metric Returns None
    [Documentation]    GIVEN bad key WHEN I get explanation THEN None
    When I Run Python Code "from lynx_utilities.metrics.explanations import get_explanation; print(get_explanation('nonexistent'))"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "None"

Get Sector Insight
    [Documentation]    GIVEN Utilities WHEN I get insight THEN data returned
    When I Run Python Code "from lynx_utilities.metrics.sector_insights import get_sector_insight; s = get_sector_insight('Utilities'); print('OK' if s else 'FAIL')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Get Industry Insight Regulated Electric
    [Documentation]    GIVEN Utilities — Regulated Electric WHEN I get insight THEN data returned
    When I Run Python Code "from lynx_utilities.metrics.sector_insights import get_industry_insight; i = get_industry_insight('Utilities — Regulated Electric'); print('OK' if i else 'FAIL')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Storage Mode Switching
    [Documentation]    GIVEN storage WHEN I switch modes THEN it works
    When I Run Python Code "from lynx_utilities.core.storage import set_mode, get_mode, is_testing; set_mode('testing'); assert is_testing(); set_mode('production'); assert not is_testing(); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Storage Invalid Mode Raises Error
    [Documentation]    GIVEN storage WHEN I set invalid mode THEN error
    When I Run Python Code "from lynx_utilities.core.storage import set_mode; set_mode('invalid')"
    Then The Exit Code Should Be 1
    Then The Output Should Contain "ValueError"

Export Formats Available
    [Documentation]    GIVEN export module WHEN I check formats THEN all exist
    When I Run Python Code "from lynx_utilities.export import ExportFormat; print(ExportFormat.TXT.value, ExportFormat.HTML.value, ExportFormat.PDF.value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "txt html pdf"

About Text Has All Fields
    [Documentation]    GIVEN package WHEN I get about THEN all fields present
    When I Run Python Code "from lynx_utilities import get_about_text; a = get_about_text(); assert all(k in a for k in ['name','suite','version','author','license','description']); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Conclusion Generation
    [Documentation]    GIVEN minimal report WHEN I generate conclusion THEN a verdict is produced
    When I Run Python Code "from lynx_utilities.models import AnalysisReport, CompanyProfile; from lynx_utilities.core.conclusion import generate_conclusion; r = AnalysisReport(profile=CompanyProfile(ticker='TEST', name='Test')); c = generate_conclusion(r); assert c.verdict in ['Strong Buy','Buy','Hold','Caution','Avoid']; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Utilities Metrics In Explanations
    [Documentation]    GIVEN explanations WHEN I list THEN utilities metrics present
    When I Run Python Code "from lynx_utilities.metrics.explanations import list_metrics; keys = [m.key for m in list_metrics()]; assert 'cash_to_market_cap' in keys; assert 'quality_score' in keys; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

New Utilities Metrics FCF Yield And CROCI Exist
    [Documentation]    GIVEN v0.4 metrics WHEN I check fcf_yield and croci THEN they exist on ValuationMetrics
    When I Run Python Code "from lynx_utilities.models import ValuationMetrics; v = ValuationMetrics(); assert hasattr(v, 'fcf_yield'); assert hasattr(v, 'croci'); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

New Utilities Metrics Capex To Revenue Exists
    [Documentation]    GIVEN v0.4 metrics WHEN I check capex_to_revenue THEN it exists on EfficiencyMetrics
    When I Run Python Code "from lynx_utilities.models import EfficiencyMetrics; e = EfficiencyMetrics(); assert hasattr(e, 'capex_to_revenue'); assert hasattr(e, 'capex_to_ocf'); assert hasattr(e, 'capex_intensity'); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

New Utilities Metrics Solvency Fields Exist
    [Documentation]    GIVEN v0.4 metrics WHEN I check solvency THEN new debt fields exist
    When I Run Python Code "from lynx_utilities.models import SolvencyMetrics; s = SolvencyMetrics(); assert hasattr(s, 'debt_per_share'); assert hasattr(s, 'net_debt_per_share'); assert hasattr(s, 'debt_service_coverage'); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

New Utilities Metrics Growth Fields Exist
    [Documentation]    GIVEN v0.4 metrics WHEN I check growth THEN new fields exist
    When I Run Python Code "from lynx_utilities.models import GrowthMetrics; g = GrowthMetrics(); assert hasattr(g, 'reinvestment_rate'); assert hasattr(g, 'dividend_payout_ratio'); assert hasattr(g, 'dividend_coverage'); assert hasattr(g, 'shareholder_yield'); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

New Utilities Metrics Profitability Fields Exist
    [Documentation]    GIVEN v0.4 metrics WHEN I check profitability THEN new fcf fields exist
    When I Run Python Code "from lynx_utilities.models import ProfitabilityMetrics; p = ProfitabilityMetrics(); assert hasattr(p, 'ocf_to_net_income'); assert hasattr(p, 'fcf_per_share'); assert hasattr(p, 'ocf_per_share'); assert hasattr(p, 'fcf_conversion'); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

New Screening Checks Capital Discipline And Dividend Covered
    [Documentation]    GIVEN v0.4 screening WHEN conclusion generated THEN new checks present
    When I Run Python Code "from lynx_utilities.models import AnalysisReport, CompanyProfile; from lynx_utilities.core.conclusion import generate_conclusion; r = AnalysisReport(profile=CompanyProfile(ticker='TEST', name='Test')); c = generate_conclusion(r); checklist = c.screening_checklist; assert 'capital_discipline' in checklist; assert 'dividend_covered' in checklist; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

AnalysisReport Uses Utilities Quality Field
    [Documentation]    GIVEN AnalysisReport WHEN I set energy_quality (schema key) THEN it accepts EnergyQualityIndicators
    When I Run Python Code "from lynx_utilities.models import AnalysisReport, CompanyProfile, EnergyQualityIndicators; eq = EnergyQualityIndicators(quality_score=75.0); r = AnalysisReport(profile=CompanyProfile(ticker='T', name='T'), energy_quality=eq); assert r.energy_quality.quality_score == 75.0; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"
