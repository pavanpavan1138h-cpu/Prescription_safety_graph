"""
tests/test_advanced_intelligence.py

Pytest suite for Phase 8 Advanced Clinical Intelligence:
Complexity analysis, cross-pair event convergence, pattern detection,
review prioritization, uncertainty mapping, and API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_single_drug_advanced_analysis(client):
    res = client.post("/api/v1/prescriptions/analyze-advanced", json={
        "medications": ["fluconazole"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["complexity_profile"]["complexity_category"] == "LOW_COMPLEXITY"
    assert data["complexity_profile"]["generated_pairs_count"] == 0
    assert len(data["clinical_context_requirements"]) >= 4

def test_two_drug_convergent_advanced_analysis(client):
    res = client.post("/api/v1/prescriptions/analyze-advanced", json={
        "medications": ["cyclosporine", "fluconazole"],
        "prescription_id": "TEST_ADV_001"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["complexity_profile"]["convergent_pairs_count"] == 1
    assert len(data["review_priorities"]) == 1
    assert data["review_priorities"][0]["review_priority"] in ["IMMEDIATE_REVIEW_PRIORITY", "HIGH_REVIEW_PRIORITY"]
    assert any(p["pattern_type"] == "CONVERGENT_EVIDENCE_CLUSTER" for p in data["evidence_patterns"])

def test_three_drug_polypharmacy_advanced_analysis(client):
    res = client.post("/api/v1/prescriptions/analyze-advanced", json={
        "medications": ["cyclosporine", "fluconazole", "phentermine"],
        "prescription_id": "TEST_ADV_002"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["complexity_profile"]["unique_drugs_count"] == 3
    assert data["complexity_profile"]["generated_pairs_count"] == 3
    assert len(data["drug_participation_profiles"]) == 3
    assert len(data["review_priorities"]) == 3
    assert len(data["advanced_explanation"]["scientific_guardrails"]) >= 4

def test_unresolved_medication_uncertainty(client):
    res = client.post("/api/v1/prescriptions/analyze-advanced", json={
        "medications": ["fluconazole", "NonExistentDrug999"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["uncertainty_profile"]["has_identity_uncertainty"] is True
    assert "NonExistentDrug999" in data["uncertainty_profile"]["unresolved_input_names"]
    assert any(p["pattern_type"] == "IDENTITY_UNCERTAINTY_PATTERN" for p in data["evidence_patterns"])

def test_no_direct_evidence_guardrails(client):
    res = client.post("/api/v1/prescriptions/analyze-advanced", json={
        "medications": ["caffeine", "phentermine"]
    })
    assert res.status_code == 200
    data = res.json()
    assert "scientific_limitations" in data
    assert len(data["scientific_limitations"]) >= 3

def test_prescription_structural_network_analysis(client):
    res = client.post("/api/v1/prescriptions/analyze-advanced", json={
        "medications": ["cyclosporine", "fluconazole", "phentermine", "trioxsalen"]
    })
    assert res.status_code == 200
    data = res.json()
    assert "structural_analysis" in data
    sa = data["structural_analysis"]
    assert sa is not None
    assert sa["network_summary"]["total_prescription_drugs"] == 4
    assert sa["network_summary"]["evidence_supported_pairs"] == 2
    assert len(sa["drug_structural_profiles"]) == 4
    assert len(sa["counterfactual_results"]) == 4
    
    # Assert isolated drugs are kept in profiles
    isolated = [dp for dp in sa["drug_structural_profiles"] if dp["evidence_degree"] == 0]
    assert len(isolated) >= 1
    assert "trioxsalen" in [dp["display_name"] for dp in isolated]
    
    # Assert counterfactual results have contribution levels
    for cf in sa["counterfactual_results"]:
        assert "contribution_level" in cf
        assert cf["contribution_level"] in ["HIGH_STRUCTURAL_IMPACT", "MODERATE_STRUCTURAL_IMPACT", "LOW_STRUCTURAL_IMPACT", "NO_STRUCTURAL_IMPACT"]

def test_prescription_evidence_intelligence(client):
    res = client.post("/api/v1/prescriptions/analyze-advanced", json={
        "medications": ["cyclosporine", "fluconazole", "phentermine", "trioxsalen"]
    })
    assert res.status_code == 200
    data = res.json()
    assert "evidence_intelligence" in data
    intel = data["evidence_intelligence"]
    assert intel is not None
    assert len(intel["themes"]) >= 1
    assert len(intel["signal_groups"]) >= 1
    assert intel["concentration_profile"]["concentration_type"] in [
        "CENTRALIZED_EVIDENCE", "CLUSTER_CONCENTRATED_EVIDENCE", "DISTRIBUTED_EVIDENCE", "MIXED_EVIDENCE_DISTRIBUTION", "SPARSE_EVIDENCE"
    ]
    assert intel["structural_evidence_alignment"]["alignment_level"] in [
        "HIGH_ALIGNMENT", "MODERATE_ALIGNMENT", "LOW_ALIGNMENT", "NO_MEANINGFUL_ALIGNMENT"
    ]
    assert "CLINICAL GUARDRAIL NOTICE" in intel["narrative"]

def test_prescription_contextual_stability(client):
    res = client.post("/api/v1/prescriptions/analyze-advanced", json={
        "medications": ["cyclosporine", "fluconazole", "phentermine", "trioxsalen"]
    })
    assert res.status_code == 200
    data = res.json()
    assert "contextual_stability" in data
    stab = data["contextual_stability"]
    assert stab is not None
    assert len(stab["scenarios"]) >= 2
    assert "overall_stability_score" in stab["evidence_stability"]
    assert len(stab["drug_dependencies"]) >= 1
    assert "overall_sensitivity_score" in stab["context_sensitivity"]
    assert stab["interpretation_stability"] in [
        "HIGH_INTERPRETATION_STABILITY", "MODERATE_INTERPRETATION_STABILITY", "LOW_INTERPRETATION_STABILITY", "FRAGILE_INTERPRETATION"
    ]
    assert "This analysis computationally changes the graph context" in stab["summary_narrative"]
