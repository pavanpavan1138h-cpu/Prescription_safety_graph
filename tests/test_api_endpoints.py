"""
tests/test_api_endpoints.py

Automated pytest suite for Phase 7 API endpoints, schema validation,
reasoning consistency, error handling, and scientific guardrails.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["graph_loaded"] is True
    assert data["reasoning_engine_available"] is True

def test_system_info(client):
    response = client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()
    assert data["graph_nodes"] == 68223
    assert data["graph_edges"] == 4969811
    assert "Drug" in data["node_breakdown"]
    assert "INTERACTS_WITH" in data["edge_breakdown"]

def test_drugs_resolve_with_duplicates(client):
    payload = {
        "drugs": ["fluconazole", "CID000003365", "DRUG_000048", "cyclosporine", "FakeDrugXYZ_123"]
    }
    response = client.post("/api/v1/drugs/resolve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["input_count"] == 5
    assert data["unique_resolved_drugs"] == 2
    assert data["duplicates_collapsed"] == 2
    assert data["unresolved_count"] == 1

def test_single_drug_entity_card(client):
    response = client.get("/api/v1/drugs/DRUG_000006")
    assert response.status_code == 200
    data = response.json()
    assert data["internal_drug_id"] == "DRUG_000006"
    assert data["display_name"].lower() == "cyclosporine"
    assert data["rxcui"] == "3008"

def test_single_drug_not_found(client):
    response = client.get("/api/v1/drugs/UnknownDrug_99999")
    assert response.status_code == 404

def test_pairwise_safety_inference(client):
    payload = {
        "drug_a": "cyclosporine",
        "drug_b": "fluconazole"
    }
    response = client.post("/api/v1/safety/pair", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["evidence_status"] == "CONVERGENT_SAFETY_EVIDENCE"
    assert data["confidence"]["level"] == "HIGH_EVIDENCE_CONFIDENCE"
    assert data["confidence"]["score"] == 0.93

def test_prescription_analysis_multi_drug(client):
    payload = {
        "medications": ["cyclosporine", "fluconazole", "phentermine"],
        "prescription_id": "TEST_RX_PYTEST"
    }
    response = client.post("/api/v1/prescriptions/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["metadata"]["analysis_id"] == "TEST_RX_PYTEST"
    assert data["prescription_summary"]["total_unique_drugs"] == 3
    assert data["prescription_summary"]["total_pairs_analyzed"] == 3
    assert data["prescription_summary"]["evidence_status"] == "MULTI_SIGNAL_EVIDENCE"
    assert len(data["prioritized_findings"]) >= 1
    
    # Guardrail check
    limitations = data["limitations"]
    assert len(limitations) > 0
    assert any("clinical risk" in l.lower() for l in limitations)
    assert any("not evidence of medical safety" in l.lower() for l in limitations)

def test_empty_prescription_rejection(client):
    response = client.post("/api/v1/prescriptions/analyze", json={"medications": []})
    assert response.status_code == 400

def test_pair_detail_drilldown(client):
    response = client.get("/api/v1/analyses/TEST_RX_PYTEST/pairs/PAIR_DRUG_000006__DRUG_000048")
    assert response.status_code == 200
    data = response.json()
    assert data["pair_id"] == "PAIR_DRUG_000006__DRUG_000048"
    assert len(data["direct_ddi_evidence"]) > 0
    assert data["combination_adverse_events"]["total_event_count"] == 202
    assert len(data["provenance_trace"]["graph_paths"]) > 0

def test_structural_endpoints_on_cached_analysis(client):
    # 1. Fetch full structural analysis
    res = client.get("/api/v1/analyses/TEST_RX_PYTEST/structure")
    assert res.status_code == 200
    data = res.json()
    assert data["analysis_id"] == "TEST_RX_PYTEST"
    assert data["network_summary"]["total_prescription_drugs"] == 3
    
    # 2. Fetch drugs
    res_drugs = client.get("/api/v1/analyses/TEST_RX_PYTEST/structure/drugs")
    assert res_drugs.status_code == 200
    drugs_data = res_drugs.json()
    assert len(drugs_data) == 3
    
    # 3. Fetch clusters
    res_clusters = client.get("/api/v1/analyses/TEST_RX_PYTEST/structure/clusters")
    assert res_clusters.status_code == 200
    clusters_data = res_clusters.json()
    assert len(clusters_data) >= 1
    
    # 4. Fetch counterfactuals
    res_cf = client.get("/api/v1/analyses/TEST_RX_PYTEST/structure/counterfactuals")
    assert res_cf.status_code == 200
    cf_data = res_cf.json()
    assert len(cf_data) == 3

def test_evidence_intelligence_endpoints_on_cached_analysis(client):
    # 1. Fetch full intelligence
    res = client.get("/api/v1/analyses/TEST_RX_PYTEST/intelligence")
    assert res.status_code == 200
    data = res.json()
    assert data["analysis_id"] == "TEST_RX_PYTEST"
    assert len(data["themes"]) >= 1

    # 2. Fetch themes
    res_themes = client.get("/api/v1/analyses/TEST_RX_PYTEST/intelligence/themes")
    assert res_themes.status_code == 200
    assert len(res_themes.json()) >= 1

    # 3. Fetch signals
    res_signals = client.get("/api/v1/analyses/TEST_RX_PYTEST/intelligence/signals")
    assert res_signals.status_code == 200
    assert len(res_signals.json()) >= 1

    # 4. Fetch concentration
    res_conc = client.get("/api/v1/analyses/TEST_RX_PYTEST/intelligence/concentration")
    assert res_conc.status_code == 200
    assert "concentration_type" in res_conc.json()

    # 5. Fetch alignment
    res_align = client.get("/api/v1/analyses/TEST_RX_PYTEST/intelligence/alignment")
    assert res_align.status_code == 200
    assert "alignment_level" in res_align.json()

def test_contextual_endpoints_on_cached_analysis(client):
    # 1. Fetch full contextual stability
    res = client.get("/api/v1/analyses/TEST_RX_PYTEST/contextual")
    assert res.status_code == 200
    data = res.json()
    assert data["analysis_id"] == "TEST_RX_PYTEST"
    assert len(data["scenarios"]) >= 1

    # 2. Fetch scenarios
    res_scen = client.get("/api/v1/analyses/TEST_RX_PYTEST/contextual/scenarios")
    assert res_scen.status_code == 200
    assert len(res_scen.json()) >= 1

    # 3. Fetch metrics
    res_metrics = client.get("/api/v1/analyses/TEST_RX_PYTEST/contextual/metrics")
    assert res_metrics.status_code == 200
    assert "overall_stability_score" in res_metrics.json()

    # 4. Fetch dependencies
    res_dep = client.get("/api/v1/analyses/TEST_RX_PYTEST/contextual/dependency")
    assert res_dep.status_code == 200
    assert len(res_dep.json()) >= 1
