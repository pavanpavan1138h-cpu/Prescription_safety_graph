from typing import List
from src.prescription.longitudinal.longitudinal_schema import (
    CrossLayerEvolutionProfile,
    LongitudinalChangePoint
)
from src.prescription.longitudinal.snapshot_sequence_engine import NormalizedSnapshotView

class CrossLayerEvolutionEngine:
    @staticmethod
    def analyze_cross_layer(
        views: List[NormalizedSnapshotView],
        change_points: List[LongitudinalChangePoint]
    ) -> CrossLayerEvolutionProfile:
        """
        Determines if multiple analytical layers shift in sync across timeline transitions.
        """
        total = len(views)
        if total < 2:
            return CrossLayerEvolutionProfile(
                structural_persistence=1.0,
                signal_persistence=1.0,
                stability_persistence=1.0,
                provenance_persistence=1.0,
                trustworthiness_persistence=1.0,
                cross_layer_transition_alignment=[],
                classification="INSUFFICIENT_HISTORY",
                explanation="Timeline requires at least 2 analytical states to evaluate multi-layer changes."
            )

        # Average persistence indices across snapshots
        topologies = [v.topology for v in views]
        top_persistence = len(set(topologies)) / total
        
        # Calculate shared participants over history (primary contributors intersection)
        shared_conts = set(views[0].primary_contributors)
        for v in views[1:]:
            shared_conts = shared_conts.intersection(v.primary_contributors)
        provenance_persistence = len(shared_conts) / max(len(views[0].primary_contributors), 1)

        # Evaluate transitions alignments
        alignments = []
        aligned_count = 0
        for cp in change_points:
            # Check if structural and signal layers changed simultaneously
            is_struct_change = cp.structural_change >= 0.35
            is_sig_change = cp.signal_change >= 0.35
            
            if is_struct_change and is_sig_change:
                alignments.append(
                    f"Transition {cp.from_snapshot_index}->{cp.to_snapshot_index}: Aligned change (Structural & Evidential)"
                )
                aligned_count += 1
            elif is_struct_change:
                alignments.append(
                    f"Transition {cp.from_snapshot_index}->{cp.to_snapshot_index}: Dimension-specific structural shift"
                )
            elif is_sig_change:
                alignments.append(
                    f"Transition {cp.from_snapshot_index}->{cp.to_snapshot_index}: Dimension-specific signal shift"
                )

        if aligned_count > 0:
            classification = "ALIGNED_MULTI_LAYER_CHANGES"
            explanation = "Multiple computational layers transitioned in sync at one or more change points."
        else:
            classification = "DIMENSION_SPECIFIC_TRANSITIONS"
            explanation = "Changes were isolated to specific individual layers without synchronized multi-layer shifts."

        return CrossLayerEvolutionProfile(
            structural_persistence=round(1.0 - top_persistence, 3),
            signal_persistence=round(provenance_persistence, 3),
            stability_persistence=round(sum(v.sensitivity for v in views) / total, 3),
            provenance_persistence=round(provenance_persistence, 3),
            trustworthiness_persistence=round(sum(v.trust_score for v in views) / total, 3),
            cross_layer_transition_alignment=alignments,
            classification=classification,
            explanation=explanation
        )
