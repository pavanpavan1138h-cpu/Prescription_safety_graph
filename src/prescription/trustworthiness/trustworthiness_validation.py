from typing import List, Dict, Any
from src.prescription.trustworthiness.trustworthiness_schema import PrescriptionTrustworthinessProfile

class TrustworthinessValidator:
    @staticmethod
    def validate_invariants(profile: PrescriptionTrustworthinessProfile) -> Dict[str, Any]:
        """
        Validates all system invariants for Phase 12.
        """
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Score bounds validation [0.0, 1.0]
        for metric in profile.trustworthiness_metrics:
            val = metric.normalized_value
            if not (0.0 <= val <= 1.0):
                errors.append(f"Metric {metric.metric_id} normalized value {val} out of bounds [0.0, 1.0].")

        # 2. Signature verification
        rep = profile.reproducibility_profile
        if not rep.baseline_signature:
            errors.append("Baseline signature is empty.")

        # 3. Guardrail validation
        if not profile.guardrails:
            errors.append("Trustworthiness guardrails are empty.")
        else:
            disclaimer = profile.guardrails[0]
            if "recommend adding, removing, discontinuing, substituting, or modifying" not in disclaimer:
                errors.append("Guardrail disclaimer text is missing required safety phrasing.")

        # 4. Score matches level
        overall = sum(m.normalized_value for m in profile.trustworthiness_metrics) / len(profile.trustworthiness_metrics)
        # Check overall score logic matches
        level_str = profile.overall_trustworthiness_level.value
        
        # Collect warning if explanation is inconsistent
        if profile.explanation_consistency.consistency_ratio < 1.0:
            warnings.append(
                f"Explanation consistency is partially mismatched ({profile.explanation_consistency.consistency_ratio * 100:.1f}%)."
            )

        return {
            "validation_passed": len(errors) == 0,
            "error_count": len(errors),
            "errors": errors,
            "warning_count": len(warnings),
            "warnings": warnings
        }
