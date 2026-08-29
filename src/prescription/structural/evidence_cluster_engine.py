"""
src/prescription/structural/evidence_cluster_engine.py

Finds connected components (evidence clusters) and calculates cluster-level metrics.
"""

from typing import List, Dict, Set, Tuple
from src.prescription.structural.prescription_network_schema import PrescriptionEvidenceNetwork, ClusterMetrics
from src.prescription.structural.structural_metrics import calculate_density

class EvidenceClusterEngine:
    @staticmethod
    def detect_clusters(network: PrescriptionEvidenceNetwork) -> List[ClusterMetrics]:
        """
        Runs connected component detection (BFS/DFS) on the prescription evidence network.
        Identifies connected components of size > 1 as evidence clusters, and size == 1 as isolated.
        """
        nodes = list(network.nodes.keys())
        
        # Build adjacency list
        adj = {n: set() for n in nodes}
        for edge_key, edge in network.edges.items():
            u, v = edge.drug_a_id, edge.drug_b_id
            if u in adj and v in adj:
                adj[u].add(v)
                adj[v].add(u)
                
        visited = set()
        components = []
        
        for node in nodes:
            if node not in visited:
                # Run BFS to extract component
                comp = []
                queue = [node]
                visited.add(node)
                
                while queue:
                    curr = queue.pop(0)
                    comp.append(curr)
                    for neighbor in adj[curr]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                            
                components.append(comp)
                
        # Build cluster metrics objects
        cluster_metrics_list = []
        cluster_counter = 1
        
        for comp in components:
            size = len(comp)
            
            # Find all internal edges belonging to this component
            comp_edges = []
            for edge_key, edge in network.edges.items():
                u, v = edge.drug_a_id, edge.drug_b_id
                if u in comp and v in comp:
                    comp_edges.append(edge)
                    
            edge_count = len(comp_edges)
            density = calculate_density(size, edge_count)
            
            # Count edge categories
            conv_count = sum(1 for e in comp_edges if e.evidence_status == "CONVERGENT_SAFETY_EVIDENCE")
            ddi_count = sum(1 for e in comp_edges if e.evidence_status == "DDI_EVIDENCE_ONLY")
            event_count = sum(1 for e in comp_edges if e.evidence_status == "COMBINATION_EVENT_EVIDENCE_ONLY")
            
            if size > 1:
                cluster_id = f"CLUSTER_{cluster_counter:03d}"
                cluster_counter += 1
                is_isolated = False
            else:
                cluster_id = f"ISOLATED_{comp[0]}"
                is_isolated = True
                
            cluster_metrics_list.append(ClusterMetrics(
                cluster_id=cluster_id,
                drug_ids=comp,
                edge_count=edge_count,
                density=round(density, 3),
                convergent_edge_count=conv_count,
                ddi_only_edge_count=ddi_count,
                combination_event_edge_count=event_count,
                is_isolated=is_isolated
            ))
            
        # Sort components: clusters first (sorted by size desc), then isolated drugs
        clusters = [c for c in cluster_metrics_list if not c.is_isolated]
        isolated = [c for c in cluster_metrics_list if c.is_isolated]
        
        clusters.sort(key=lambda x: (len(x.drug_ids), x.edge_count), reverse=True)
        isolated.sort(key=lambda x: x.cluster_id)
        
        return clusters + isolated
