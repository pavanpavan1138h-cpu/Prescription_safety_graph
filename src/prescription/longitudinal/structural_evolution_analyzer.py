from typing import List
from src.prescription.longitudinal.longitudinal_schema import (
    StructuralEvolutionProfile,
    StructuralEvolutionLevel,
    LongitudinalChangePoint
)
from src.prescription.longitudinal.snapshot_sequence_engine import NormalizedSnapshotView

class StructuralEvolutionAnalyzer:
    @staticmethod
    def analyze_structure(
        views: List[NormalizedSnapshotView],
        change_points: List[LongitudinalChangePoint]
    ) -> StructuralEvolutionProfile:
        """
        Extracts structural evolution parameters and classifications.
        """
        total = len(views)
        if total < 2:
            return StructuralEvolutionProfile(
                topology_sequence=[],
                density_sequence=[],
                central_participant_sequence=[],
                cluster_count_sequence=[],
                topology_transition_count=0,
                structural_change_points=[],
                classification=StructuralEvolutionLevel.INSUFFICIENT_STRUCTURAL_HISTORY
            )

        topologies = [v.topology for v in views]
        densities = [v.density for v in views]
        clusters = [v.cluster_count for v in views]
        participants = [v.central_participants for v in views]

        # Topology transitions count
        transitions = 0
        for i in range(1, total):
            if topologies[i - 1] != topologies[i]:
                transitions += 1

        # Identify structural change points (transitions where structural_change >= 0.35)
        struct_cp_indices = []
        for cp in change_points:
            if cp.structural_change >= 0.35:
                struct_cp_indices.append(cp.to_snapshot_index)

        # Classification mapping rules
        if transitions == 0 and len(struct_cp_indices) == 0:
            classification = StructuralEvolutionLevel.STRUCTURALLY_STABLE
        elif transitions <= 1 and len(struct_cp_indices) <= 1:
            classification = StructuralEvolutionLevel.GRADUAL_STRUCTURAL_EVOLUTION
        elif len(struct_cp_indices) >= 3 or transitions >= 3:
            classification = StructuralEvolutionLevel.HIGH_STRUCTURAL_VOLATILITY
        else:
            classification = StructuralEvolutionLevel.STRUCTURAL_RECONFIGURATION

        return StructuralEvolutionProfile(
            topology_sequence=topologies,
            density_sequence=[round(d, 3) for d in densities],
            central_participant_sequence=participants,
            cluster_count_sequence=clusters,
            topology_transition_count=transitions,
            structural_change_points=struct_cp_indices,
            classification=classification
        )
