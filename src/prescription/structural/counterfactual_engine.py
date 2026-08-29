"""
src/prescription/structural/counterfactual_engine.py

Simulates the hypothetical computational removal of each drug from the evidence network
and quantifies the structural impact on network connectivity.
"""

from typing import List
from copy import deepcopy
from src.prescription.structural.prescription_network_schema import (
    PrescriptionEvidenceNetwork,
    PrescriptionEvidenceNode,
    PrescriptionEvidenceEdge,
    ClusterMetrics,
    CounterfactualResult,
    StructuralImpactLevel
)
from src.prescription.structural.evidence_cluster_engine import EvidenceClusterEngine

class CounterfactualEngine:
    @staticmethod
    def run_analysis(
        original_network: PrescriptionEvidenceNetwork,
        original_clusters: List[ClusterMetrics]
    ) -> List[CounterfactualResult]:
        """
        Simulates the removal of each drug node and its incident edges one-by-one.
        Computes the delta in edge and component structure to determine structural impact.
        """
        results = []
        original_edge_count = len(original_network.edges)
        original_conv_count = sum(1 for e in original_network.edges.values() if e.evidence_status == "CONVERGENT_SAFETY_EVIDENCE")
        
        # Calculate cluster sizes for active clusters
        active_orig_clusters = [c for c in original_clusters if not c.is_isolated]
        orig_cluster_count = len(active_orig_clusters)
        orig_largest_cluster = len(active_orig_clusters[0].drug_ids) if active_orig_clusters else 0
        
        for drug_id, node in original_network.nodes.items():
            # 1. Create simulated sub-network (excluding drug_id)
            sim_nodes = {k: v for k, v in original_network.nodes.items() if k != drug_id}
            sim_edges = {}
            for edge_key, edge in original_network.edges.items():
                if edge.drug_a_id != drug_id and edge.drug_b_id != drug_id:
                    sim_edges[edge_key] = edge
                    
            sim_network = PrescriptionEvidenceNetwork(
                nodes=sim_nodes,
                edges=sim_edges,
                canonical_drug_ids=[did for did in original_network.canonical_drug_ids if did != drug_id]
            )
            
            # 2. Detect clusters on simulated network
            sim_clusters = EvidenceClusterEngine.detect_clusters(sim_network)
            active_sim_clusters = [c for c in sim_clusters if not c.is_isolated]
            
            sim_edge_count = len(sim_edges)
            sim_conv_count = sum(1 for e in sim_edges.values() if e.evidence_status == "CONVERGENT_SAFETY_EVIDENCE")
            sim_cluster_count = len(active_sim_clusters)
            sim_largest_cluster = len(active_sim_clusters[0].drug_ids) if active_sim_clusters else 0
            
            # 3. Calculate deltas
            edge_delta = original_edge_count - sim_edge_count
            conv_delta = original_conv_count - sim_conv_count
            
            # 4. Classify Structural Impact Level
            if edge_delta == 0:
                impact = StructuralImpactLevel.NO_STRUCTURAL_IMPACT
            elif edge_delta >= 3 or conv_delta >= 1 or sim_cluster_count > orig_cluster_count or (orig_largest_cluster - sim_largest_cluster) >= 2:
                impact = StructuralImpactLevel.HIGH_STRUCTURAL_IMPACT
            elif edge_delta == 2 or (orig_largest_cluster - sim_largest_cluster) == 1:
                impact = StructuralImpactLevel.MODERATE_STRUCTURAL_IMPACT
            else:
                impact = StructuralImpactLevel.LOW_STRUCTURAL_IMPACT
                
            # 5. Generate Explanation
            exp = (
                f"Computational exclusion of {node.display_name} removes {edge_delta} evidence-supported "
                f"relationship(s) and {conv_delta} convergent safety channel(s)."
            )
            
            results.append(CounterfactualResult(
                drug_id=drug_id,
                display_name=node.display_name,
                original_edge_count=original_edge_count,
                remaining_edge_count=sim_edge_count,
                structural_delta=edge_delta,
                convergent_edges_removed=conv_delta,
                clusters_before=orig_cluster_count,
                clusters_after=sim_cluster_count,
                largest_cluster_before=orig_largest_cluster,
                largest_cluster_after=sim_largest_cluster,
                contribution_level=impact,
                explanation=exp
            ))
            
        return results
