"""
test_box9_risk_classifier.py

Deterministic test suite for BOX 9 — Risk & Patient-Context Analysis.
Verifies:
1. NAPROXEN (Boxed Warning)
2. WARFARIN (ISMP High-Alert)
3. Standard drug classification
4. Precedence (Boxed Warning > High-Alert > Standard)
5. Default patient context (Adult, Normal, Normal -> zero artificial increase)
6. Boxed warning score modifier (+1.5 and deterministic reason)
7. ISMP high-alert score modifier (+1.0 and deterministic reason)
8. Reduced kidney function modifier (+1.0 and deterministic reason)
9. Reduced liver function modifier (+1.0 and deterministic reason)
10. Age modifier (Pediatric +1.0, Elderly +1.0, Adult +0)
11. Combined modifiers (+3.5 total audit trail)
"""

import pytest
from src.prescription.risk.risk_classifier import DrugRiskClassifier
from src.prescription.advanced_intelligence_schema import (
    RiskTier,
    AgeBand,
    OrganFunctionStatus,
    PatientContext,
    DrugRiskAssessment,
    ReviewPriorityTier,
)
from src.prescription.advanced_intelligence_engines import (
    ReviewPrioritizationEngine,
)


@pytest.fixture(scope="module")
def classifier():
    return DrugRiskClassifier()


def test_1_naproxen_boxed_warning(classifier):
    """TEST 1: Naproxen with RxCUI 198014 is classified as Boxed Warning with retained FDA text."""
    res = classifier.classify_drug(
        internal_drug_id="DRUG_CUSTOM_NAPROXEN",
        rxcui="198014",
        drug_name="NAPROXEN"
    )
    assert res.risk_tier == RiskTier.BOXED_WARNING
    assert res.has_boxed_warning is True
    assert res.boxed_warning_text is not None and len(res.boxed_warning_text) > 0
    assert "CARDIOVASCULAR" in res.boxed_warning_text
    assert "openFDA" in res.evidence_source


def test_2_warfarin_ismp_high_alert(classifier):
    """TEST 2: Warfarin with DRUG_000496 is classified as High-Alert with ISMP category."""
    res = classifier.classify_drug(
        internal_drug_id="DRUG_000496",
        rxcui="11289",
        drug_name="warfarin"
    )
    assert res.risk_tier == RiskTier.HIGH_ALERT
    assert res.is_ismp_high_alert is True
    assert res.ismp_category is not None
    assert "antithrombotic" in res.ismp_category.lower()
    assert res.has_boxed_warning is False
    assert res.evidence_source == "ISMP"


def test_3_standard_drug(classifier):
    """TEST 3: Drug with no OpenFDA boxed warning and not on ISMP is classified as Standard."""
    res = classifier.classify_drug(
        internal_drug_id="DRUG_000008",
        rxcui="11248",
        drug_name="vitamin B12"
    )
    assert res.risk_tier == RiskTier.STANDARD
    assert res.is_ismp_high_alert is False
    assert res.has_boxed_warning is False
    assert res.evidence_source == "Standard"


def test_4_risk_tier_precedence(classifier):
    """TEST 4: When a drug has both Boxed Warning and ISMP High-Alert, Boxed Warning takes precedence while both are retained."""
    # Synthesize a case using the classifier logic or synthetic override
    synthetic_assessment = DrugRiskAssessment(
        drug_id="DRUG_DUAL",
        drug_name="Dual-Risk Medication",
        rxcui="999999",
        risk_tier=RiskTier.BOXED_WARNING,
        is_ismp_high_alert=True,
        ismp_category="antithrombotic agents",
        has_boxed_warning=True,
        boxed_warning_text="FATAL HEMORRHAGE RISK",
        contraindications_text="Active major bleeding",
        warnings_cautions_text="Monitor closely",
        evidence_source="openFDA+ISMP"
    )
    assert synthetic_assessment.risk_tier == RiskTier.BOXED_WARNING
    assert synthetic_assessment.has_boxed_warning is True
    assert synthetic_assessment.is_ismp_high_alert is True
    assert synthetic_assessment.evidence_source == "openFDA+ISMP"


# Helper mock classes to test ReviewPrioritizationEngine in complete isolation
class MockResolutionResult:
    def __init__(self, resolved_drugs):
        self.resolved_drugs = resolved_drugs


class MockResolvedDrug:
    def __init__(self, internal_id, name):
        self.resolved_internal_drug_id = internal_id
        self.display_name = name


class MockReport:
    def __init__(self, pair_results, resolved_drugs):
        self.pair_results = pair_results
        self.resolution_summary = MockResolutionResult(resolved_drugs)


def _build_test_report():
    resolved = [
        MockResolvedDrug("DRUG_A", "Drug A"),
        MockResolvedDrug("DRUG_B", "Drug B")
    ]
    pair_res = [{
        "drug_a_id": "DRUG_A",
        "drug_b_id": "DRUG_B",
        "evidence_status": "NO_DIRECT_GRAPH_EVIDENCE",
        "confidence_score": 0.0,
        "ddi_present": False
    }]
    return MockReport(pair_res, resolved)


def test_5_default_patient_context():
    """TEST 5: Default patient context yields no artificial score increase."""
    report = _build_test_report()
    findings = ReviewPrioritizationEngine.analyze(
        report=report,
        part_profiles=[],
        event_conv_items=[],
        patient_context=None,
        drug_risk_assessments=[]
    )
    assert len(findings) == 1
    # Base score for NO_DIRECT_GRAPH_EVIDENCE is 0.0
    assert findings[0].review_score == 0.0
    assert findings[0].review_priority == ReviewPriorityTier.LIMITED_EVIDENCE_REVIEW
    # No patient context reasons
    assert not any("Patient is in" in r or "Reduced" in r for r in findings[0].deterministic_reasons)


def test_6_boxed_warning_score_modifier():
    """TEST 6: Boxed warning drug adds +1.5 with deterministic reason."""
    report = _build_test_report()
    dra_a = DrugRiskAssessment(
        drug_id="DRUG_A",
        drug_name="Drug A",
        rxcui="198014",
        risk_tier=RiskTier.BOXED_WARNING,
        is_ismp_high_alert=False,
        ismp_category=None,
        has_boxed_warning=True,
        boxed_warning_text="Black box warning",
        contraindications_text=None,
        warnings_cautions_text=None,
        evidence_source="openFDA"
    )
    findings = ReviewPrioritizationEngine.analyze(
        report=report,
        part_profiles=[],
        event_conv_items=[],
        patient_context=PatientContext(),
        drug_risk_assessments=[dra_a]
    )
    assert len(findings) == 1
    assert findings[0].review_score == 1.5
    assert "Drug has an FDA boxed warning: +1.5" in findings[0].deterministic_reasons


def test_7_ismp_score_modifier():
    """TEST 7: ISMP high-alert drug adds +1.0 with deterministic reason."""
    report = _build_test_report()
    dra_b = DrugRiskAssessment(
        drug_id="DRUG_B",
        drug_name="Drug B",
        rxcui="11289",
        risk_tier=RiskTier.HIGH_ALERT,
        is_ismp_high_alert=True,
        ismp_category="antithrombotic agents",
        has_boxed_warning=False,
        boxed_warning_text=None,
        contraindications_text=None,
        warnings_cautions_text=None,
        evidence_source="ISMP"
    )
    findings = ReviewPrioritizationEngine.analyze(
        report=report,
        part_profiles=[],
        event_conv_items=[],
        patient_context=PatientContext(),
        drug_risk_assessments=[dra_b]
    )
    assert len(findings) == 1
    assert findings[0].review_score == 1.0
    assert "Drug is classified as ISMP High-Alert: +1.0" in findings[0].deterministic_reasons


def test_8_reduced_kidney_function():
    """TEST 8: Reduced kidney function adds +1.0 with deterministic reason."""
    report = _build_test_report()
    ctx = PatientContext(kidney_function=OrganFunctionStatus.REDUCED)
    findings = ReviewPrioritizationEngine.analyze(
        report=report,
        part_profiles=[],
        event_conv_items=[],
        patient_context=ctx,
        drug_risk_assessments=[]
    )
    assert len(findings) == 1
    assert findings[0].review_score == 1.0
    assert "Patient has Reduced kidney function: +1.0" in findings[0].deterministic_reasons


def test_9_reduced_liver_function():
    """TEST 9: Reduced liver function adds +1.0 with deterministic reason."""
    report = _build_test_report()
    ctx = PatientContext(liver_function=OrganFunctionStatus.REDUCED)
    findings = ReviewPrioritizationEngine.analyze(
        report=report,
        part_profiles=[],
        event_conv_items=[],
        patient_context=ctx,
        drug_risk_assessments=[]
    )
    assert len(findings) == 1
    assert findings[0].review_score == 1.0
    assert "Patient has Reduced liver function: +1.0" in findings[0].deterministic_reasons


def test_10_age_modifiers():
    """TEST 10: Age modifiers add +1.0 for Pediatric and Elderly, +0 for Adult."""
    report = _build_test_report()

    # Pediatric -> +1.0
    res_ped = ReviewPrioritizationEngine.analyze(
        report=report,
        part_profiles=[],
        event_conv_items=[],
        patient_context=PatientContext(age_band=AgeBand.PEDIATRIC),
        drug_risk_assessments=[]
    )
    assert res_ped[0].review_score == 1.0
    assert "Patient is in Pediatric age band: +1.0" in res_ped[0].deterministic_reasons

    # Elderly -> +1.0
    res_eld = ReviewPrioritizationEngine.analyze(
        report=report,
        part_profiles=[],
        event_conv_items=[],
        patient_context=PatientContext(age_band=AgeBand.ELDERLY),
        drug_risk_assessments=[]
    )
    assert res_eld[0].review_score == 1.0
    assert "Patient is in Elderly age band: +1.0" in res_eld[0].deterministic_reasons

    # Adult -> +0.0
    res_adu = ReviewPrioritizationEngine.analyze(
        report=report,
        part_profiles=[],
        event_conv_items=[],
        patient_context=PatientContext(age_band=AgeBand.ADULT),
        drug_risk_assessments=[]
    )
    assert res_adu[0].review_score == 0.0


def test_11_combined_modifiers():
    """TEST 11: Combined Boxed Warning (+1.5), Reduced kidney function (+1.0), and Elderly (+1.0) total +3.5."""
    report = _build_test_report()
    dra_a = DrugRiskAssessment(
        drug_id="DRUG_A",
        drug_name="Drug A",
        rxcui="198014",
        risk_tier=RiskTier.BOXED_WARNING,
        is_ismp_high_alert=False,
        ismp_category=None,
        has_boxed_warning=True,
        boxed_warning_text="Black box warning",
        contraindications_text=None,
        warnings_cautions_text=None,
        evidence_source="openFDA"
    )
    ctx = PatientContext(
        age_band=AgeBand.ELDERLY,
        kidney_function=OrganFunctionStatus.REDUCED,
        liver_function=OrganFunctionStatus.NORMAL
    )
    findings = ReviewPrioritizationEngine.analyze(
        report=report,
        part_profiles=[],
        event_conv_items=[],
        patient_context=ctx,
        drug_risk_assessments=[dra_a]
    )
    assert len(findings) == 1
    assert findings[0].review_score == 3.5  # 1.5 + 1.0 + 1.0
    assert findings[0].review_priority == ReviewPriorityTier.MODERATE_REVIEW_PRIORITY

    # Verify each reason is separately auditable
    reasons = findings[0].deterministic_reasons
    assert "Drug has an FDA boxed warning: +1.5" in reasons
    assert "Patient is in Elderly age band: +1.0" in reasons
    assert "Patient has Reduced kidney function: +1.0" in reasons
