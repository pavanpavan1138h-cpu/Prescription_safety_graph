"""
tests/test_longitudinal.py

Automated pytest suite for Phase 13 Longitudinal Evolution Engine.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_longitudinal_evolution_pipeline_and_endpoints(client):
    # 1. Trigger three sequential snapshots to create history in cache
    res1 = client.post("/api/v1/prescriptions/analyze-advanced", json={
        "medications": ["cyclosporine", "fluconazole"]
    })
    assert res1.status_code == 200
    id1 = res1.json()["prescription_report"]["metadata"]["analysis_id"]

    res2 = client.post("/api/v1/prescriptions/analyze-advanced", json={
        "medications": ["cyclosporine", "fluconazole", "phentermine"]
    })
    assert res2.status_code == 200
    id2 = res2.json()["prescription_report"]["metadata"]["analysis_id"]

    res3 = client.post("/api/v1/prescriptions/analyze-advanced", json={
        "medications": ["cyclosporine", "phentermine"]
    })
    assert res3.status_code == 200
    id3 = res3.json()["prescription_report"]["metadata"]["analysis_id"]

    # 2. Trigger longitudinal compilation
    res_post = client.post("/api/v1/analyses/longitudinal", json={
        "analysis_ids": [id1, id2, id3]
    })
    assert res_post.status_code == 200
    long_id = res_post.json()["longitudinal_id"]
    assert long_id is not None

    # 3. Request complete longitudinal profile
    res_prof = client.get(f"/api/v1/longitudinal/{long_id}")
    assert res_prof.status_code == 200
    data = res_prof.json()
    assert len(data["timeline"]) == 3
    assert len(data["change_points"]) == 2
    assert "This longitudinal evaluation describes how the computational" in data["guardrails"][0]
    assert data["overall_evolution_level"] is not None

    # 4. Request sub-properties
    res_timeline = client.get(f"/api/v1/longitudinal/{long_id}/timeline")
    assert res_timeline.status_code == 200
    assert len(res_timeline.json()) == 3

    res_persistence = client.get(f"/api/v1/longitudinal/{long_id}/persistence")
    assert res_persistence.status_code == 200
    assert len(res_persistence.json()) > 0

    res_emergence = client.get(f"/api/v1/longitudinal/{long_id}/emergence")
    assert res_emergence.status_code == 200

    res_disappearance = client.get(f"/api/v1/longitudinal/{long_id}/disappearance")
    assert res_disappearance.status_code == 200

    res_cp = client.get(f"/api/v1/longitudinal/{long_id}/change-points")
    assert res_cp.status_code == 200
    assert len(res_cp.json()) == 2

    res_struct = client.get(f"/api/v1/longitudinal/{long_id}/structure")
    assert res_struct.status_code == 200
    assert "density_sequence" in res_struct.json()

    res_signals = client.get(f"/api/v1/longitudinal/{long_id}/signals")
    assert res_signals.status_code == 200
    assert isinstance(res_signals.json(), list)

    res_stability = client.get(f"/api/v1/longitudinal/{long_id}/stability")
    assert res_stability.status_code == 200
    assert "sensitivity_sequence" in res_stability.json()

    res_trust = client.get(f"/api/v1/longitudinal/{long_id}/trustworthiness")
    assert res_trust.status_code == 200
    assert "score_sequence" in res_trust.json()

    res_cl = client.get(f"/api/v1/longitudinal/{long_id}/cross-layer")
    assert res_cl.status_code == 200
    assert "structural_persistence" in res_cl.json()

def test_missing_longitudinal_profile_error(client):
    res = client.get("/api/v1/longitudinal/NON_EXISTENT_LONG_ID")
    assert res.status_code == 404
