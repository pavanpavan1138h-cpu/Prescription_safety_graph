"""
tests/test_trustworthiness.py

Automated pytest suite for Phase 12 Robustness, Evaluation
and Computational Trustworthiness Intelligence Engine.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_trustworthiness_evaluation_pipeline_and_endpoints(client):
    # 1. Trigger advanced prescription analysis
    res = client.post("/api/v1/prescriptions/analyze-advanced", json={
        "medications": ["cyclosporine", "fluconazole", "phentermine"]
    })
    assert res.status_code == 200
    data = res.json()
    analysis_id = data["prescription_report"]["metadata"]["analysis_id"]

    # Verify trustworthiness payload is embedded in advanced response
    assert "trustworthiness" in data
    trust = data["trustworthiness"]
    assert trust is not None
    assert trust["analysis_id"] == analysis_id
    assert 0.0 <= trust["trustworthiness_metrics"][0]["value"] <= 1.0
    assert "This evaluation measures the computational robustness" in trust["guardrails"][0]
    assert "reproducibility_profile" in trust
    assert "input_perturbation_results" in trust

    # 2. Test sub-endpoints
    res_trust = client.get(f"/api/v1/analyses/{analysis_id}/trustworthiness")
    assert res_trust.status_code == 200
    assert res_trust.json()["overall_trustworthiness_level"] is not None

    res_repro = client.get(f"/api/v1/analyses/{analysis_id}/trustworthiness/reproducibility")
    assert res_repro.status_code == 200
    assert "baseline_signature" in res_repro.json()

    res_perts = client.get(f"/api/v1/analyses/{analysis_id}/trustworthiness/perturbations")
    assert res_perts.status_code == 200
    assert len(res_perts.json()) > 0

    res_struct = client.get(f"/api/v1/analyses/{analysis_id}/trustworthiness/structure")
    assert res_struct.status_code == 200
    assert "topology_persistence_ratio" in res_struct.json()

    res_sigs = client.get(f"/api/v1/analyses/{analysis_id}/trustworthiness/signals")
    assert res_sigs.status_code == 200
    assert isinstance(res_sigs.json(), list)

    res_cl = client.get(f"/api/v1/analyses/{analysis_id}/trustworthiness/cross-layer")
    assert res_cl.status_code == 200
    assert "shared_participants" in res_cl.json()

    res_prov = client.get(f"/api/v1/analyses/{analysis_id}/trustworthiness/provenance")
    assert res_prov.status_code == 200
    assert "traceability_coverage" in res_prov.json()

    res_exp = client.get(f"/api/v1/analyses/{analysis_id}/trustworthiness/explanation-consistency")
    assert res_exp.status_code == 200
    assert "consistency_ratio" in res_exp.json()

def test_missing_analysis_trustworthiness_error(client):
    res = client.get("/api/v1/analyses/NON_EXISTENT_ANALYSIS/trustworthiness")
    assert res.status_code == 404
