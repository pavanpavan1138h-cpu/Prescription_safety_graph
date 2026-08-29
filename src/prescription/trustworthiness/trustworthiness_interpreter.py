from typing import List
from src.prescription.trustworthiness.trustworthiness_schema import (
    ReproducibilityProfile,
    StructuralRobustnessProfile,
    CrossLayerConsistencyProfile,
    ProvenanceCompletenessProfile,
    ExplanationConsistencyProfile,
    TrustworthinessLevel
)

class TrustworthinessInterpreter:
    @staticmethod
    def generate_narrative(
        score: float,
        level: TrustworthinessLevel,
        reproducibility: ReproducibilityProfile,
        structure: StructuralRobustnessProfile,
        consistency: CrossLayerConsistencyProfile,
        provenance: ProvenanceCompletenessProfile,
        explanation: ExplanationConsistencyProfile
    ) -> str:
        """
        Generates the deterministic narrative report of the trustworthiness profile,
        focusing strictly on computational stability metrics.
        """
        parts: List[str] = []
        
        parts.append(
            f"The prescription safety graph analysis pipeline completed evaluation with an overall computational "
            f"trustworthiness score of {score:.2f} ({level.value.replace('_', ' ')})."
        )

        # Reproducibility
        parts.append(
            f"Deterministic verification classified repeat runs as {reproducibility.classification.value.replace('_', ' ')} "
            f"with a match ratio of {reproducibility.deterministic_match_ratio * 100:.1f}%."
        )

        # Structure
        parts.append(
            f"Under contextual perturbations, the baseline evidence topology classification '{structure.baseline_topology}' "
            f"demonstrated a persistence ratio of {structure.topology_persistence_ratio * 100:.1f}%. "
            f"Structural hubs and cluster mappings were evaluated as {structure.robustness_level.value.replace('_', ' ')}."
        )

        # Consistency
        parts.append(
            f"Cross-layer convergence checks classified participant overlapping behavior as "
            f"'{consistency.consistency_level.value}'. {consistency.explanation}"
        )

        # Provenance & Explanation
        parts.append(
            f"Provenance and grounding coverage reached {provenance.traceability_coverage * 100:.1f}% "
            f"with {provenance.orphaned_component_count} orphaned nodes. "
            f"Explanation claims were found to be {explanation.classification.replace('_', ' ')} "
            f"({explanation.claims_supported} of {explanation.claims_checked} claims verified against source graphs)."
        )

        return "\n\n".join(parts)

    @staticmethod
    def get_guardrails() -> List[str]:
        return [
            "This evaluation measures the computational robustness, consistency, traceability, and reproducibility of the analytical system. It does not establish clinical correctness, patient safety, therapeutic superiority, or medical certainty, and it does not recommend adding, removing, discontinuing, substituting, or modifying medication therapy."
        ]
