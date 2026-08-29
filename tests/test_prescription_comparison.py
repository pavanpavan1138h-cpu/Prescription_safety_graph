import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_prescription_comparison_flow(client):
    # 1. Generate snapshot A
    res_a = client.post("/api/v1/prescriptions/analyze-advanced", json={
        "medications": ["cyclosporine", "fluconazole", "phentermine"]
    })
    assert res_a.status_code == 200
    id_a = res_a.json()["prescription_report"]["metadata"]["analysis_id"]

    # 2. Generate snapshot B
    res_b = client.post("/api/v1/prescriptions/analyze-advanced", json={
        "medications": ["cyclosporine", "fluconazole", "trioxsalen"]
    })
    assert res_b.status_code == 200
    id_b = res_b.json()["prescription_report"]["metadata"]["analysis_id"]

    # 3. Compare A vs B
    res_comp = client.post("/api/v1/prescriptions/compare", json={
        "analysis_id_a": id_a,
        "analysis_id_b": id_b
    })
    assert res_comp.status_code == 200
    data = res_comp.json()
    
    comp_id = data["comparison_id"]
    assert comp_id.startswith("COMP_")
    assert data["analysis_id_a"] == id_a
    assert data["analysis_id_b"] == id_b
    assert len(data["medication_set_comparison"]["shared_drugs"]) == 2
    assert len(data["medication_set_comparison"]["a_only_drugs"]) == 1
    assert len(data["medication_set_comparison"]["b_only_drugs"]) == 1

    # Assert structural magnitude exists
    assert "structural_delta_magnitude" in data["structural_delta"]
    assert 0.0 <= data["structural_delta"]["structural_delta_magnitude"] <= 1.0

    # Assert structured major changes are populated
    assert len(data["major_changes"]) >= 1
    for mc in data["major_changes"]:
        assert mc["category"] in ["EVIDENCE", "STRUCTURE", "SIGNAL", "STABILITY"]
        assert "change_type" in mc
        assert "magnitude" in mc
        assert "description" in mc

    # Assert clinical safety notice warning disclaimer presence
    assert "This comparison describes differences between computational evidence states" in data["narrative"]
    assert len(data["guardrails"]) >= 1

    # 4. Fetch sub-resources
    res_ev = client.get(f"/api/v1/comparisons/{comp_id}/evidence")
    assert res_ev.status_code == 200
    assert "added_pairs_count" in res_ev.json()

    res_st = client.get(f"/api/v1/comparisons/{comp_id}/structure")
    assert res_st.status_code == 200
    assert "node_count_delta" in res_st.json()

    res_sig = client.get(f"/api/v1/comparisons/{comp_id}/signals")
    assert res_sig.status_code == 200
    assert "concentration_changed" in res_sig.json()

    res_stab = client.get(f"/api/v1/comparisons/{comp_id}/stability")
    assert res_stab.status_code == 200
    assert "stability_change_type" in res_stab.json()

def test_identical_snapshot_comparison(client):
    res_a = client.post("/api/v1/prescriptions/analyze-advanced", json={
        "medications": ["cyclosporine", "fluconazole", "phentermine"]
    })
    id_a = res_a.json()["prescription_report"]["metadata"]["analysis_id"]

    res_comp = client.post("/api/v1/prescriptions/compare", json={
        "analysis_id_a": id_a,
        "analysis_id_b": id_a
    })
    assert res_comp.status_code == 200
    data = res_comp.json()
    assert data["summary"]["global_delta_interpretation"] == "IDENTICAL_SNAPSHOTS"
    assert data["structural_delta"]["structural_delta_magnitude"] == 0.0
    assert data["evidence_delta"]["added_pairs_count"] == 0
    assert data["evidence_delta"]["removed_pairs_count"] == 0
    assert data["evidence_delta"]["reclassified_pairs_count"] == 0

def test_missing_snapshot_error(client):
    res = client.post("/api/v1/prescriptions/compare", json={
        "analysis_id_a": "MISSING_ID_A",
        "analysis_id_b": "MISSING_ID_B"
    })
    assert res.status_code == 400
    assert "not found in the service cache" in res.json()["error"]["message"]

def test_missing_comparison_id_lookup(client):
    res = client.get("/api/v1/comparisons/COMP_MISSING")
    assert res.status_code == 404
