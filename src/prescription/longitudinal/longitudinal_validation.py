from typing import Dict, Any
from src.prescription.longitudinal.longitudinal_schema import PrescriptionLongitudinalProfile

class LongitudinalValidation:
    @staticmethod
    def validate_invariants(
        profile: PrescriptionLongitudinalProfile
    ) -> Dict[str, Any]:
        """
        Validates all system invariants for Phase 13.
        """
        errors = []
        warnings = []

        # Invariant 1: Persistence bounds [0, 1]
        for p in profile.persistence_profiles:
            if not (0.0 <= p.presence_ratio <= 1.0):
                errors.append(f"Persistence profile {p.entity_id} presence ratio {p.presence_ratio} out of bounds [0.0, 1.0].")

        # Invariant 2: Change point scores bounds [0, 1]
        for cp in profile.change_points:
            score = cp.aggregate_change_score
            if not (0.0 <= score <= 1.0):
                errors.append(f"Change point {cp.from_snapshot_index}->{cp.to_snapshot_index} aggregate score {score} out of bounds [0.0, 1.0].")

        # Invariant 3: Guardrail existence and safety content
        if not profile.guardrails:
            errors.append("Longitudinal guardrails are empty.")
        else:
            disclaimer = profile.guardrails[0]
            if "recommend adding, removing, discontinuing, substituting, or modifying" not in disclaimer:
                errors.append("Guardrail disclaimer text is missing required safety phrasing.")
            if "does not establish clinical progression" not in disclaimer:
                errors.append("Guardrail disclaimer must disavow clinical progression claims.")

        # Invariant 4: Check that no clinical outcome predictions are in the summary text
        clinical_keywords = ["clinically better", "treatment improved", "patient improved", "healed", "deteriorated"]
        summary = profile.longitudinal_summary.lower()
        for kw in clinical_keywords:
            if kw in summary:
                errors.append(f"Summary contains illegal clinical outcome word: '{kw}'")

        # Invariant 5: Timeline ordering
        prev_idx = -1
        for ref in profile.timeline:
            if ref.sequence_index <= prev_idx:
                errors.append(f"Timeline reference index ordering is not strictly ascending (index {ref.sequence_index} follows {prev_idx}).")
            prev_idx = ref.sequence_index

        return {
            "validation_passed": len(errors) == 0,
            "error_count": len(errors),
            "errors": errors,
            "warning_count": len(warnings),
            "warnings": warnings
        }
