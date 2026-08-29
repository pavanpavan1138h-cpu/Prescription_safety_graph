"""
src/prescription/structural/drug_participation_analyzer.py

Analyzes each drug's role in the network and computes structural profiles and contribution scores.
"""

from typing import List, Dict
from src.prescription.structural.prescription_network_schema import (
    PrescriptionEvidenceNetwork,
    ClusterMetrics,
    DrugStructuralProfile
)
from src.prescription.structural.structural_metrics import calculate_degrees, calculate_betweenness_centrality

class DrugParticipationAnalyzer:
    @staticmethod
    def analyze(network: PrescriptionEvidenceNetwork, clusters: List[ClusterMetrics]) -> List[DrugStructuralProfile]:
        """
        Creates a structural profile for each drug node in the network.
        Ranks drugs and assigns structural contribution levels.
        """
        nodes = list(network.nodes.keys())
        
        # 1. Map edges to tuples for degree calculation
        edge_tuples = []
        unweighted_edges = []
        for edge in network.edges.values():
            edge_tuples.append((edge.drug_a_id, edge.drug_b_id, edge.edge_strength))
            unweighted_edges.append((edge.drug_a_id, edge.drug_b_id))
            
        degrees, weighted_degrees = calculate_degrees(nodes, edge_tuples)
        betweenness = calculate_betweenness_centrality(nodes, unweighted_edges)
        
        # Build node-to-cluster mapping
        node_to_cluster = {}
        node_to_cluster_size = {}
        for c in clusters:
            for drug in c.drug_ids:
                node_to_cluster[drug] = c.cluster_id
                node_to_cluster_size[drug] = len(c.drug_ids)
                
        profiles = []
        max_weighted_deg = max(weighted_degrees.values()) if weighted_degrees.values() else 0.0
        total_edges = len(network.edges)
        
        for drug_id in nodes:
            node = network.nodes[drug_id]
            deg = degrees[drug_id]
            w_deg = weighted_degrees[drug_id]
            bet = betweenness[drug_id]
            
            # Normalize degree centrality
            deg_centrality = 0.0
            if len(nodes) > 1:
                deg_centrality = float(deg) / (len(nodes) - 1)
                
            # Count incident edge evidence channels
            convergent_count = 0
            ddi_count = 0
            event_count = 0
            channels = set()
            
            for edge in network.edges.values():
                if edge.drug_a_id == drug_id or edge.drug_b_id == drug_id:
                    if edge.evidence_status == "CONVERGENT_SAFETY_EVIDENCE":
                        convergent_count += 1
                        channels.add("CONVERGENT")
                    elif edge.evidence_status == "DDI_EVIDENCE_ONLY":
                        ddi_count += 1
                        channels.add("DDI")
                    elif edge.evidence_status == "COMBINATION_EVENT_EVIDENCE_ONLY":
                        event_count += 1
                        channels.add("EVENT")
                        
            diversity = len(channels)
            
            # Calculate composite score
            # Score components:
            # - 40% Normalized weighted degree
            # - 30% Betweenness centrality
            # - 20% Evidence channel diversity
            # - 10% Convergent edge count
            norm_w_deg = (w_deg / max_weighted_deg) if max_weighted_deg > 0.0 else 0.0
            norm_diversity = diversity / 3.0
            norm_conv = (convergent_count / total_edges) if total_edges > 0 else 0.0
            
            score = (0.40 * norm_w_deg) + (0.30 * bet) + (0.20 * norm_diversity) + (0.10 * norm_conv)
            score = round(score, 3)
            
            # Map score to structural contribution level
            if score >= 0.6:
                level = "HIGH_STRUCTURAL_CONTRIBUTION"
            elif score >= 0.3:
                level = "MODERATE_STRUCTURAL_CONTRIBUTION"
            elif score >= 0.1:
                level = "LOW_STRUCTURAL_CONTRIBUTION"
            else:
                level = "MINIMAL_STRUCTURAL_CONTRIBUTION"
                
            # Explanation
            exp = (
                f"Participates in {deg} evidence-supported relationship(s) "
                f"across {diversity} evidence channel(s) with degree centrality "
                f"of {deg_centrality:.2f}."
            )
            
            profiles.append(DrugStructuralProfile(
                drug_id=drug_id,
                display_name=node.display_name,
                evidence_degree=deg,
                weighted_evidence_degree=round(w_deg, 3),
                degree_centrality=round(deg_centrality, 3),
                betweenness_centrality=round(bet, 3),
                evidence_channel_diversity=diversity,
                convergent_relationship_count=convergent_count,
                ddi_only_relationship_count=ddi_count,
                combination_only_relationship_count=event_count,
                cluster_id=node_to_cluster.get(drug_id, "UNASSIGNED"),
                cluster_size=node_to_cluster_size.get(drug_id, 1),
                centrality_rank=0,  # assigned later after sorting
                structural_contribution_level=level,
                structural_contribution_score=score,
                explanation=exp
            ))
            
        # Rank profiles (1-indexed) based on score desc, then degree desc
        profiles.sort(key=lambda x: (x.structural_contribution_score, x.weighted_evidence_degree), reverse=True)
        for i, profile in enumerate(profiles, 1):
            profile.centrality_rank = i
            
        return profiles
