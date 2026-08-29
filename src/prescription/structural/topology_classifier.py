"""
src/prescription/structural/topology_classifier.py

Classifies the topology of the prescription evidence network into primary and secondary classifications.
"""

from typing import List
from src.prescription.structural.prescription_network_schema import (
    PrescriptionEvidenceNetwork,
    ClusterMetrics,
    TopologyType,
    TopologyClassification
)

class TopologyClassifier:
    @staticmethod
    def classify(network: PrescriptionEvidenceNetwork, clusters: List[ClusterMetrics]) -> TopologyClassification:
        """
        Runs deterministic heuristic rules to classify network topology.
        Supports primary topology classification and secondary characteristic flags.
        """
        total_edges = len(network.edges)
        total_drugs = len(network.nodes)
        
        # 1. Edge count checks
        if total_edges == 0:
            return TopologyClassification(
                primary_topology=TopologyType.NO_EVIDENCE_NETWORK,
                secondary_characteristics=["ISOLATED_DRUG_PRESENT"] if total_drugs > 0 else []
            )
            
        # Separate clusters (size > 1) and isolated drugs (size == 1)
        active_clusters = [c for c in clusters if not c.is_isolated]
        isolated_drugs = [c for c in clusters if c.is_isolated]
        
        secondary_chars = []
        if len(isolated_drugs) > 0:
            secondary_chars.append("ISOLATED_DRUG_PRESENT")
            
        # Check for convergent edges
        has_convergent = any(e.evidence_status == "CONVERGENT_SAFETY_EVIDENCE" for e in network.edges.values())
        if has_convergent:
            secondary_chars.append("CONVERGENT_EVIDENCE_PRESENT")
        else:
            secondary_chars.append("SINGLE_CHANNEL_ONLY_NETWORK")
            
        # Helper to check if a cluster is star-centric
        def is_cluster_star(cluster: ClusterMetrics) -> bool:
            if len(cluster.drug_ids) < 3:
                return False
            # Find degrees of drugs inside this cluster
            degrees = {}
            for drug in cluster.drug_ids:
                deg = sum(1 for e in network.edges.values() if (e.drug_a_id == drug or e.drug_b_id == drug) and e.drug_a_id in cluster.drug_ids and e.drug_b_id in cluster.drug_ids)
                degrees[drug] = deg
            
            sorted_degs = sorted(degrees.values(), reverse=True)
            max_deg = sorted_degs[0]
            # Star-centric conditions:
            # - Max degree node connects to almost all nodes in the cluster
            # - Max degree is at least twice the second highest degree (if second highest exists and is > 0)
            if max_deg >= 3:
                if len(sorted_degs) > 1 and (sorted_degs[1] == 0 or max_deg >= 2 * sorted_degs[1]):
                    return True
                if max_deg == len(cluster.drug_ids) - 1 and all(d == 1 for d in sorted_degs[1:]):
                    return True
            return False
            
        # Helper to check if a cluster is dense
        def is_cluster_dense(cluster: ClusterMetrics) -> bool:
            return len(cluster.drug_ids) >= 3 and cluster.density >= 0.8
            
        # Scan clusters for characteristics
        star_clusters = [c for c in active_clusters if is_cluster_star(c)]
        dense_clusters = [c for c in active_clusters if is_cluster_dense(c)]
        
        if star_clusters:
            secondary_chars.append("STAR_CENTRIC_CLUSTER_PRESENT")
        if dense_clusters:
            secondary_chars.append("DENSE_EVIDENCE_CLUSTER_PRESENT")
            
        # 2. Topology rules
        
        # Scenario A: All clusters have size == 2 and edge == 1
        if len(active_clusters) > 0 and all(len(c.drug_ids) == 2 for c in active_clusters):
            return TopologyClassification(
                primary_topology=TopologyType.ISOLATED_PAIR_EVIDENCE,
                secondary_characteristics=secondary_chars
            )
            
        # Scenario B: Multiple disconnected clusters of size > 1
        if len(active_clusters) > 1:
            return TopologyClassification(
                primary_topology=TopologyType.MULTIPLE_EVIDENCE_CLUSTERS,
                secondary_characteristics=secondary_chars
            )
            
        # Scenario C: Exactly 1 active cluster
        if len(active_clusters) == 1:
            main_cluster = active_clusters[0]
            
            # Check if this main cluster is star-centric
            if is_cluster_star(main_cluster):
                return TopologyClassification(
                    primary_topology=TopologyType.STAR_CENTRIC_STRUCTURE,
                    secondary_characteristics=secondary_chars
                )
                
            # Check if this main cluster is dense
            if is_cluster_dense(main_cluster):
                return TopologyClassification(
                    primary_topology=TopologyType.DENSE_EVIDENCE_CLUSTER,
                    secondary_characteristics=secondary_chars
                )
                
            # Default single cluster
            return TopologyClassification(
                primary_topology=TopologyType.SINGLE_CONNECTED_CLUSTER,
                secondary_characteristics=secondary_chars
            )
            
        # Default fallback
        return TopologyClassification(
            primary_topology=TopologyType.SINGLE_CONNECTED_CLUSTER,
            secondary_characteristics=secondary_chars
        )
