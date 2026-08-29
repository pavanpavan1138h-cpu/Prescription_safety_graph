from typing import List
from src.prescription.longitudinal.longitudinal_schema import (
    StabilityEvolutionProfile,
    StabilityEvolutionLevel
)
from src.prescription.longitudinal.snapshot_sequence_engine import NormalizedSnapshotView

class StabilityEvolutionAnalyzer:
    @staticmethod
    def analyze_stability(
        views: List[NormalizedSnapshotView]
    ) -> StabilityEvolutionProfile:
        """
        Processes contextual stability history classifications.
        """
        total = len(views)
        if total < 2:
            return StabilityEvolutionProfile(
                stability_sequence=[],
                sensitivity_sequence=[],
                transition_count=0,
                classification=StabilityEvolutionLevel.INSUFFICIENT_LONGITUDINAL_CONTEXT
            )

        stability_seq = [v.stability for v in views]
        sensitivity_seq = [v.sensitivity for v in views]

        # Count state changes
        transitions = 0
        for i in range(1, total):
            if stability_seq[i - 1] != stability_seq[i]:
                transitions += 1

        # Classify transitions
        if transitions == 0:
            if "CONTEXT_SENSITIVE" in stability_seq[0]:
                classification = StabilityEvolutionLevel.FLUCTUATING_STABILITY
            else:
                classification = StabilityEvolutionLevel.CONSISTENTLY_STABLE
        elif transitions == 1:
            if "CONTEXT_SENSITIVE" in stability_seq[-1]:
                classification = StabilityEvolutionLevel.STABLE_TO_CONTEXT_SENSITIVE
            else:
                classification = StabilityEvolutionLevel.CONTEXT_SENSITIVE_TO_STABLE
        else:
            classification = StabilityEvolutionLevel.FLUCTUATING_STABILITY

        return StabilityEvolutionProfile(
            stability_sequence=stability_seq,
            sensitivity_sequence=[round(s, 3) for s in sensitivity_seq],
            transition_count=transitions,
            classification=classification
        )
