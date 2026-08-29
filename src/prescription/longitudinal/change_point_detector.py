from typing import List, Set
from src.prescription.longitudinal.longitudinal_schema import (
    LongitudinalChangePoint,
    ChangePointLevel
)
from src.prescription.longitudinal.snapshot_sequence_engine import NormalizedSnapshotView

class ChangePointDetector:
    @staticmethod
    def detect_change_points(
        views: List[NormalizedSnapshotView]
    ) -> List[LongitudinalChangePoint]:
        """
        Calculates aggregate change score between adjacent snapshot views.
        """
        change_points: List[LongitudinalChangePoint] = []
        total = len(views)
        if total < 2:
            return change_points

        for idx in range(1, total):
            v1 = views[idx - 1]
            v2 = views[idx]

            # 1. Medication set change
            set1 = set(v1.medications)
            set2 = set(v2.medications)
            union = set1.union(set2)
            if union:
                med_change = len(set1.symmetric_difference(set2)) / len(union)
            else:
                med_change = 0.0

            # 2. Structural change
            topo_change = 1.0 if v1.topology != v2.topology else 0.0
            density_change = abs(v1.density - v2.density)
            cluster_change = abs(v1.cluster_count - v2.cluster_count) / max(v1.cluster_count, v2.cluster_count, 1)
            struct_change = (topo_change * 0.5) + (density_change * 0.25) + (cluster_change * 0.25)

            # 3. Signal change
            themes1 = set(v1.themes.keys())
            themes2 = set(v2.themes.keys())
            theme_union = themes1.union(themes2)
            if theme_union:
                sig_change = len(themes1.symmetric_difference(themes2)) / len(theme_union)
            else:
                sig_change = 0.0

            # 4. Stability change
            stab_change = 1.0 if v1.stability != v2.stability else abs(v1.sensitivity - v2.sensitivity)
            stab_change = min(1.0, max(0.0, stab_change))

            # 5. Trustworthiness change
            trust_change = abs(v1.trust_score - v2.trust_score)

            # Aggregate Score:
            # 0.20 * med + 0.25 * struct + 0.20 * sig + 0.15 * stab + 0.20 * trust
            overall = (
                (0.20 * med_change) +
                (0.25 * struct_change) +
                (0.20 * sig_change) +
                (0.15 * stab_change) +
                (0.20 * trust_change)
            )
            overall = round(max(0.0, min(1.0, overall)), 3)

            # Determine Level
            if overall >= 0.80:
                level = ChangePointLevel.COMPOSITE_CHANGE_POINT
            elif overall >= 0.60:
                level = ChangePointLevel.MAJOR_CHANGE
            elif overall >= 0.35:
                level = ChangePointLevel.MODERATE_CHANGE
            elif overall >= 0.10:
                level = ChangePointLevel.MINOR_CHANGE
            else:
                level = ChangePointLevel.NO_SIGNIFICANT_CHANGE

            # Contributing dimensions list
            dims = []
            if med_change > 0.0: dims.append("MEDICATIONS")
            if struct_change >= 0.3: dims.append("STRUCTURE")
            if sig_change >= 0.3: dims.append("SIGNAL")
            if stab_change >= 0.3: dims.append("STABILITY")
            if trust_change >= 0.15: dims.append("TRUSTWORTHINESS")

            change_points.append(LongitudinalChangePoint(
                from_snapshot_index=v1.sequence_index,
                to_snapshot_index=v2.sequence_index,
                structural_change=round(struct_change, 3),
                signal_change=round(sig_change, 3),
                stability_change=round(stab_change, 3),
                trustworthiness_change=round(trust_change, 3),
                medication_set_change=round(med_change, 3),
                aggregate_change_score=overall,
                change_level=level,
                contributing_dimensions=dims
            ))

        return change_points
