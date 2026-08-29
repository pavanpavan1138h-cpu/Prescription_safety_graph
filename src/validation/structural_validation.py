"""
src/prescription/structural/structural_validation.py

Verification and validation suite for Phase 8 Prescription Structural analysis.
Assures invariants, accounting, and graph metric bounds.
"""

import logging
from typing import List, Dict, Any
from src.prescription.structural.prescription_network_schema import (
    PrescriptionEvidenceNetwork,
    PrescriptionStructuralAnalysis,
    ClusterMetrics,
    DrugStructuralProfile
)
from src.prescription.schemas import PrescriptionSafetyReport

logger = logging.getLogger(__name__)

class StructuralValidator:
    @staticmethod
    def validate_analysis(
        analysis: PrescriptionStructuralAnalysis,
        report: PrescriptionSafetyReport
    ) -> Dict[str, Any]:
        """
        Validates the output of a Prescription Structural Analysis.
        Returns a dict of validation results and a status boolean.
        """
        errors = []
        warnings = []
        
        orig_net = analysis.original_network
        
        # 1. Node Accounting Check
        resolved_ids = set(d.resolved_internal_drug_id for d in report.resolution_summary.resolved_drugs if d.resolved_internal_drug_id)
        network_nodes = set(orig_net.nodes.keys())
        if resolved_ids != network_nodes:
            errors.append(f"Node mismatch: Resolution summary has {resolved_ids}, but network has {network_nodes}")
            
        # 2. Edge Accounting Check
        expected_edges = 0
        for p in report.pair_results:
            if p.get("evidence_status") != "NO_DIRECT_GRAPH_EVIDENCE":
                expected_edges += 1
        if len(orig_net.edges) != expected_edges:
            errors.append(f"Edge mismatch: Expected {expected_edges} edges, found {len(orig_net.edges)}")
            
        # 3. Cluster Node Partitioning Check
        # Nodes must be partitioned exactly: every node in exactly one cluster
        all_cluster_nodes = []
        for c in analysis.clusters:
            all_cluster_nodes.extend(c.drug_ids)
            
        # Check duplicates
        if len(all_cluster_nodes) != len(set(all_cluster_nodes)):
            errors.append("Cluster partitioning overlap: Some drugs are assigned to multiple connected components.")
        if set(all_cluster_nodes) != network_nodes:
            errors.append(f"Cluster partitioning incomplete: Cluster nodes {set(all_cluster_nodes)} != Network nodes {network_nodes}")
            
        # 4. Centrality bounds check [0.0 - 1.0]
        for dp in analysis.drug_structural_profiles:
            if not (0.0 <= dp.degree_centrality <= 1.001):
                errors.append(f"Degree centrality for {dp.display_name} out of bounds: {dp.degree_centrality}")
            if not (0.0 <= dp.betweenness_centrality <= 1.001):
                errors.append(f"Betweenness centrality for {dp.display_name} out of bounds: {dp.betweenness_centrality}")
                
        # 5. Ranks check (must be unique and from 1 to N)
        ranks = [dp.centrality_rank for dp in analysis.drug_structural_profiles]
        if sorted(ranks) != list(range(1, len(network_nodes) + 1)):
            errors.append(f"Centrality ranks are invalid or non-contiguous: {ranks}")
            
        # 6. Counterfactual immutability verification
        # Ensure counterfactual exclusions haven't mutated original network sizes
        if len(orig_net.nodes) != len(resolved_ids):
            errors.append("Counterfactual execution mutated original network node counts.")
        if len(orig_net.edges) != expected_edges:
            errors.append("Counterfactual execution mutated original network edge counts.")
            
        status = len(errors) == 0
        
        return {
            "validation_passed": status,
            "error_count": len(errors),
            "errors": errors,
            "warning_count": len(warnings),
            "warnings": warnings,
            "network_stats": {
                "nodes": len(network_nodes),
                "edges": len(orig_net.edges),
                "clusters": len(analysis.clusters)
            }
        }
