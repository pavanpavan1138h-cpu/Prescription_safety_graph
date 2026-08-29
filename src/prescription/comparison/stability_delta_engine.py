from typing import Any
from src.prescription.comparison.comparison_schema import (
    StabilityDelta,
    StabilityChangeType
)

class StabilityDeltaEngine:
    @staticmethod
    def compare(
        stab_a: Any,
        stab_b: Any
    ) -> StabilityDelta:
        score_a = stab_a.evidence_stability.overall_stability_score
        score_b = stab_b.evidence_stability.overall_stability_score
        score_delta = score_b - score_a

        sens_a = stab_a.context_sensitivity.overall_sensitivity_score
        sens_b = stab_b.context_sensitivity.overall_sensitivity_score
        sens_delta = sens_b - sens_a

        level_a = stab_a.interpretation_stability.value if hasattr(stab_a.interpretation_stability, "value") else str(stab_a.interpretation_stability)
        level_b = stab_b.interpretation_stability.value if hasattr(stab_b.interpretation_stability, "value") else str(stab_b.interpretation_stability)

        # Map to rank stability
        rank_map = {
            "HIGH_INTERPRETATION_STABILITY": 4,
            "MODERATE_INTERPRETATION_STABILITY": 3,
            "LOW_INTERPRETATION_STABILITY": 2,
            "FRAGILE_INTERPRETATION": 1
        }

        r_a = rank_map.get(level_a, 0)
        r_b = rank_map.get(level_b, 0)

        if r_b > r_a:
            change = StabilityChangeType.STABILITY_INCREASED
        elif r_b < r_a:
            change = StabilityChangeType.STABILITY_DECREASED
        else:
            change = StabilityChangeType.UNCHANGED

        return StabilityDelta(
            stability_score_a=score_a,
            stability_score_b=score_b,
            stability_score_delta=score_delta,
            sensitivity_score_a=sens_a,
            sensitivity_score_b=sens_b,
            sensitivity_score_delta=sens_delta,
            interpretation_stability_a=level_a,
            interpretation_stability_b=level_b,
            stability_change_type=change
        )
