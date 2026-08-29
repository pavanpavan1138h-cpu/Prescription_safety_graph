"""
tests/test_explainability.py

Automated pytest suite for Phase 11 Evidence Provenance, Traceability
and Explainability Intelligence Engine.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_explainability_pipeline_and_endpoints(client):
    # 1. Run advanced analysis
    res = client.post("/api/v1/prescriptions/analyze-advanced", json={
        "medications": ["cyclosporine", "fluconazole", "phentermine"]
    })
    assert res.status_code == 200
    data = res.json()
    analysis_id = data["prescription_report"]["metadata"]["analysis_id"]

    assert "explainability" in data
    exp = data["explainability"]
    assert exp is not None
    assert exp["analysis_id"] == analysis_id
    assert len(exp["explanation_graph"]["nodes"]) >= 3
    assert len(exp["explanation_graph"]["edges"]) >= 2
    assert len(exp["provenance_records"]) >= 1
    assert 0.0 <= exp["traceability_profile"]["traceability_coverage_score"] <= 1.0
    assert len(exp["contribution_profiles"]) >= 1
    assert "This explanation describes how the computational system derived" in exp["narrative"]

    # 2. Test dedicated sub-endpoints
    res_exp = client.get(f"/api/v1/analyses/{analysis_id}/explainability")
    assert res_exp.status_code == 200
    assert res_exp.json()["analysis_id"] == analysis_id

    res_graph = client.get(f"/api/v1/analyses/{analysis_id}/explainability/graph")
    assert res_graph.status_code == 200
    assert len(res_graph.json()["nodes"]) > 0

    res_prov = client.get(f"/api/v1/analyses/{analysis_id}/explainability/provenance")
    assert res_prov.status_code == 200
    assert isinstance(res_prov.json(), list)

    res_contrib = client.get(f"/api/v1/analyses/{analysis_id}/explainability/contributors")
    assert res_contrib.status_code == 200
    assert len(res_contrib.json()) > 0
    top_c = res_contrib.json()[0]
    assert 0.0 <= top_c["overall_contribution_score"] <= 1.0

    res_dep = client.get(f"/api/v1/analyses/{analysis_id}/explainability/dependencies")
    assert res_dep.status_code == 200
    assert res_dep.json()["acyclic_verified"] is True

    res_trace = client.get(f"/api/v1/analyses/{analysis_id}/explainability/traceability")
    assert res_trace.status_code == 200
    assert "traceability_coverage_score" in res_trace.json()

def test_missing_analysis_explainability_error(client):
    res = client.get("/api/v1/analyses/NON_EXISTENT_ANALYSIS/explainability")
    assert res.status_code == 404
