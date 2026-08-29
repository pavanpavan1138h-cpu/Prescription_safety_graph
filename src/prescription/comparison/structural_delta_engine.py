from typing import Any, List, Dict, Optional, Set
from src.prescription.comparison.comparison_schema import (
    StructuralDelta,
    DrugRankComparison
)
from src.prescription.comparison.normalization_engine import NormalizationEngine

class StructuralDeltaEngine:
    @staticmethod
    def compare(
        struct_a: Any,
        struct_b: Any,
        drugs_a_set: Set[str],
        drugs_b_set: Set[str]
    ) -> StructuralDelta:
        # A summary stats
        na = struct_a.network_summary.total_prescription_drugs
        ea = struct_a.network_summary.evidence_supported_pairs
        da = struct_a.network_summary.network_density
        ca = struct_a.network_summary.connected_cluster_count
        ta = struct_a.topology.primary_topology.value
        dom_a = struct_a.structural_interpretation.highest_participation_drug

        # B summary stats
        nb = struct_b.network_summary.total_prescription_drugs
        eb = struct_b.network_summary.evidence_supported_pairs
        db = struct_b.network_summary.network_density
        cb = struct_b.network_summary.connected_cluster_count
        tb = struct_b.topology.primary_topology.value
        dom_b = struct_b.structural_interpretation.highest_participation_drug

        node_delta = nb - na
        edge_delta = eb - ea
        density_delta = db - da
        cluster_delta = cb - ca
        topology_changed = ta != tb
        dominant_drug_changed = dom_a != dom_b

        # Centrality Rank Movement
        profiles_a = {p.drug_id: p for p in struct_a.drug_structural_profiles}
        profiles_b = {p.drug_id: p for p in struct_b.drug_structural_profiles}

        all_drugs = drugs_a_set.union(drugs_b_set)
        rank_comparisons: List[DrugRankComparison] = []

        for drug_id in sorted(all_drugs):
            pa = profiles_a.get(drug_id)
            pb = profiles_b.get(drug_id)

            rank_a = pa.centrality_rank if pa else None
            rank_b = pb.centrality_rank if pb else None
            display_name = pb.display_name if pb else (pa.display_name if pa else drug_id)

            norm_a = NormalizationEngine.normalized_rank_position(rank_a, na) if rank_a else None
            norm_b = NormalizationEngine.normalized_rank_position(rank_b, nb) if rank_b else None

            rank_diff = None
            norm_diff = None

            if rank_a is not None and rank_b is not None:
                rank_diff = rank_a - rank_b  # positive indicates shift up in centrality
                norm_diff = norm_a - norm_b

            rank_comparisons.append(DrugRankComparison(
                drug_id=drug_id,
                display_name=display_name,
                rank_a=rank_a,
                rank_b=rank_b,
                rank_delta=rank_diff,
                normalized_position_a=norm_a,
                normalized_position_b=norm_b,
                normalized_position_delta=norm_diff
            ))

        # STRUCTURAL_DELTA_MAGNITUDE Calculation
        d_nodes = abs(node_delta) / max(1, na + nb)
        d_edges = abs(edge_delta) / max(1, ea + eb)
        d_density = abs(density_delta)
        d_topology = 0.5 if topology_changed else 0.0
        d_cluster = abs(cluster_delta) / max(1, ca + cb)

        magnitude = min(1.0, 0.2 * d_nodes + 0.3 * d_edges + 0.1 * d_density + 0.2 * d_topology + 0.2 * d_cluster)

        return StructuralDelta(
            node_count_a=na,
            node_count_b=nb,
            node_count_delta=node_delta,
            edge_count_a=ea,
            edge_count_b=eb,
            edge_count_delta=edge_delta,
            density_a=da,
            density_b=db,
            density_delta=density_delta,
            cluster_count_a=ca,
            cluster_count_b=cb,
            cluster_count_delta=cluster_delta,
            topology_a=ta,
            topology_b=tb,
            topology_changed=topology_changed,
            dominant_drug_a=dom_a,
            dominant_drug_b=dom_b,
            dominant_drug_changed=dominant_drug_changed,
            rank_comparisons=rank_comparisons,
            structural_delta_magnitude=round(magnitude, 3)
        )
