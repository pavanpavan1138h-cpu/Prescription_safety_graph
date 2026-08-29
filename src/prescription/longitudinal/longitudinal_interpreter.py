from typing import List
from src.prescription.longitudinal.longitudinal_schema import (
    LongitudinalEvolutionLevel,
    StructuralEvolutionProfile,
    StabilityEvolutionProfile,
    TrustworthinessEvolutionProfile
)

class LongitudinalInterpreter:
    @staticmethod
    def generate_narrative(
        snapshots_count: int,
        overall_level: LongitudinalEvolutionLevel,
        change_point_count: int,
        structure: StructuralEvolutionProfile,
        stability: StabilityEvolutionProfile,
        trustworthiness: TrustworthinessEvolutionProfile
    ) -> str:
        """
        Generates a deterministic longitudinal analytical summary of the timeline evolution.
        """
        parts = []
        
        parts.append(
            f"Across {snapshots_count} ordered analytical snapshots, the computational profile demonstrated "
            f"an overall progression level of '{overall_level.value.replace('_', ' ')}'."
        )

        parts.append(
            f"The system detected {change_point_count} major change point transitions. "
            f"Structural topology was classified as '{structure.classification.value.replace('_', ' ')}' "
            f"with {structure.topology_transition_count} topology transition occurrences."
        )

        parts.append(
            f"The contextual stability profile transitioned as '{stability.classification.value.replace('_', ' ')}', "
            f"indicating shift trends under pertubative checks. "
            f"Computational trustworthiness maintained a mean score of {trustworthiness.mean_score:.2f} "
            f"({trustworthiness.classification.value.replace('_', ' ')})."
        )

        return "\n\n".join(parts)

    @staticmethod
    def get_guardrails() -> List[str]:
        return [
            "This longitudinal evaluation describes how the computational analytical profile changes across available prescription snapshots. It does not establish clinical progression, patient improvement or deterioration, medication efficacy, therapeutic superiority, patient safety, or medical correctness, and it does not recommend adding, removing, discontinuing, substituting, or modifying medication therapy."
        ]
