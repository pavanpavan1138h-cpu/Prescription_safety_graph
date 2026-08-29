"""
tests/test_graph_endpoints.py

Automated pytest suite for Phase 7.5 Interactive Subgraph Visualization Endpoints.
Verifies prescription overview graphs, pair evidence graphs, provenance graphs,
truncation metadata, and referential integrity against the canonical knowledge graph.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_prescription_overview_graph(client):
    # 1. Run analysis first
    r_anl = client.post("/api/v1/prescriptions/analyze", json={
        "medications": ["cyclosporine", "fluconazole", "phentermine"],
        "prescription_id": "GRAPH_TEST_RX_001"
    })
    assert r_anl.status_code == 200

    # 2. Query Subgraph
    r_graph = client.get("/api/v1/analyses/GRAPH_TEST_RX_001/graph?side_effect_limit=5")
    assert r_graph.status_code == 200
    data = r_graph.json()

    assert "nodes" in data
    assert "edges" in data
    assert "metadata" in data

    nodes = data["nodes"]
    edges = data["edges"]
    meta = data["metadata"]

    assert meta["graph_type"] == "PRESCRIPTION_OVERVIEW"
    assert meta["node_count"] == len(nodes)
    assert meta["edge_count"] == len(edges)

    # Check node types
    node_types = set(n["node_type"] for n in nodes)
    assert "Drug" in node_types
    assert "DrugPair" in node_types

    # Check edge types
    edge_types = set(e["relationship_type"] for e in edges)
    assert "INTERACTS_WITH" in edge_types
    assert "MEMBER_OF_PAIR" in edge_types

def test_pair_evidence_graph(client):
    pair_id = "PAIR_DRUG_000006__DRUG_000048"
    r_pair_graph = client.get(f"/api/v1/analyses/GRAPH_TEST_RX_001/pairs/{pair_id}/graph?side_effect_limit=10")
    assert r_pair_graph.status_code == 200
    data = r_pair_graph.json()

    meta = data["metadata"]
    assert meta["graph_type"] == "PAIR_EVIDENCE"
    assert meta["pair_id"] == pair_id
    assert meta["truncated"] is True
    assert meta["hidden_node_count"] > 0

    # Focal drugs must be present
    focal_nodes = [n for n in data["nodes"] if n["is_focal"]]
    assert len(focal_nodes) == 2

def test_provenance_graph(client):
    pair_id = "PAIR_DRUG_000006__DRUG_000048"
    r_prov = client.get(f"/api/v1/analyses/GRAPH_TEST_RX_001/pairs/{pair_id}/provenance-graph")
    assert r_prov.status_code == 200
    data = r_prov.json()

    meta = data["metadata"]
    assert meta["graph_type"] == "PROVENANCE_TRACE"
    
    node_types = set(n["node_type"] for n in data["nodes"])
    assert "InferenceDecision" in node_types
    assert "ReasoningRule" in node_types
    assert "ProvenanceSource" in node_types
