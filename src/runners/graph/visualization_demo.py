"""
src/run_graph_visualization_demo.py

Demonstration runner for Phase 7.5 Interactive Knowledge Graph Subgraph Layer.
Tests:
1. Prescription Overview Subgraph generation.
2. Pair Evidence Subgraph with controlled side-effect truncation.
3. Multi-Hop Decision Provenance Subgraph.
"""

import json
import logging
from pathlib import Path
from fastapi.testclient import TestClient
from src.api.main import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_demo():
    client = TestClient(app)
    logger.info("================================================================================")
    logger.info("PRESCRIPTION SAFETY PLATFORM — PHASE 7.5 INTERACTIVE GRAPH VISUALIZATION DEMO")
    logger.info("================================================================================")

    # 1. Analyze 3-Drug Prescription
    logger.info("\n--- 1. Analyzing Prescription (cyclosporine + fluconazole + phentermine) ---")
    r_anl = client.post("/api/v1/prescriptions/analyze", json={
        "medications": ["cyclosporine", "fluconazole", "phentermine"],
        "prescription_id": "GRAPH_DEMO_RX_001"
    })
    anl_data = r_anl.json()
    logger.info(f"Prescription Status: {anl_data['prescription_summary']['evidence_status']}")
    logger.info(f"Total Drugs: {anl_data['prescription_summary']['total_unique_drugs']} | Total Pairs: {anl_data['prescription_summary']['total_pairs_analyzed']}")

    # 2. Extract Prescription Overview Subgraph
    logger.info("\n--- 2. Fetching Prescription Overview Subgraph (/analyses/{id}/graph) ---")
    r_ov = client.get("/api/v1/analyses/GRAPH_DEMO_RX_001/graph?side_effect_limit=5")
    ov_data = r_ov.json()
    logger.info(f"Graph Type: {ov_data['metadata']['graph_type']}")
    logger.info(f"Nodes Extracted: {ov_data['metadata']['node_count']} | Edges Extracted: {ov_data['metadata']['edge_count']}")
    logger.info(f"Node Categories: {[n['display_category'] for n in ov_data['nodes'][:6]]}")
    logger.info(f"Relationships: {set(e['relationship_type'] for e in ov_data['edges'])}")

    # 3. Extract Focused Pair Evidence Subgraph
    logger.info("\n--- 3. Fetching Pair Evidence Subgraph (/pairs/{id}/graph) ---")
    pair_id = "PAIR_DRUG_000006__DRUG_000048"
    r_pair = client.get(f"/api/v1/analyses/GRAPH_DEMO_RX_001/pairs/{pair_id}/graph?side_effect_limit=15")
    pair_data = r_pair.json()
    logger.info(f"Focused Pair: {pair_data['metadata']['pair_id']}")
    logger.info(f"Evidence Nodes: {pair_data['metadata']['node_count']} | Edges: {pair_data['metadata']['edge_count']}")
    logger.info(f"Side-Effect Truncation Active: {pair_data['metadata']['truncated']} (+{pair_data['metadata']['hidden_node_count']} hidden nodes)")

    # 4. Extract Multi-Hop Provenance Subgraph
    logger.info("\n--- 4. Fetching Decision Provenance Subgraph (/pairs/{id}/provenance-graph) ---")
    r_prov = client.get(f"/api/v1/analyses/GRAPH_DEMO_RX_001/pairs/{pair_id}/provenance-graph")
    prov_data = r_prov.json()
    logger.info(f"Provenance Graph Type: {prov_data['metadata']['graph_type']}")
    logger.info(f"Inference & Provenance Nodes: {[n['label'] for n in prov_data['nodes']]}")
    logger.info(f"Provenance Trace Edges: {[e['label'] + ' (' + e['source_dataset'] + ')' for e in prov_data['edges']]}")

    logger.info("\n================================================================================")
    logger.info("PHASE 7.5 INTERACTIVE GRAPH VISUALIZATION DEMO COMPLETED SUCCESSFULLY!")
    logger.info("================================================================================")

if __name__ == "__main__":
    run_demo()
