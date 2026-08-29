from typing import List, Dict, Any
from src.prescription.longitudinal.longitudinal_schema import (
    DisappearanceEvent,
    DisappearanceClassification
)
from src.prescription.longitudinal.snapshot_sequence_engine import NormalizedSnapshotView

class DisappearanceAnalyzer:
    @staticmethod
    def analyze_disappearance(
        views: List[NormalizedSnapshotView]
    ) -> List[DisappearanceEvent]:
        """
        Scans sequence to identify when drugs or evidence themes disappear.
        """
        events: List[DisappearanceEvent] = []
        total = len(views)
        if total < 2:
            return events

        # Helper structure to trace presence per entity
        entity_occurrences: Dict[str, Dict[str, Any]] = {}

        # Scan for medications presence
        for idx, view in enumerate(views):
            for med in view.medications:
                DisappearanceAnalyzer._record_presence(entity_occurrences, med, "DRUG", idx)

        # Scan for themes presence
        for idx, view in enumerate(views):
            for theme_id in view.themes.keys():
                DisappearanceAnalyzer._record_presence(entity_occurrences, theme_id, "EVIDENCE_THEME", idx)

        # Evaluate disappearances
        for entity_id, info in entity_occurrences.items():
            presence = info["presence"]
            # Fill missing trailing slots to match total
            while len(presence) < total:
                presence.append(False)

            # Find first transition (present -> absent)
            for idx in range(1, total):
                if presence[idx - 1] and not presence[idx]:
                    # Disappearance transition detected at idx!
                    previously_present_count = sum(1 for p in presence[:idx] if p)
                    post_disappearance_snapshots = presence[idx:]
                    post_disappearance_absence_ratio = sum(1 for p in post_disappearance_snapshots if not p) / len(post_disappearance_snapshots)

                    # Classify disappearance
                    if post_disappearance_absence_ratio >= 0.80:
                        classification = DisappearanceClassification.PERSISTENTLY_DISAPPEARED
                    elif post_disappearance_absence_ratio <= 0.35:
                        classification = DisappearanceClassification.RECURRENTLY_PRESENT
                    else:
                        classification = DisappearanceClassification.TEMPORARILY_ABSENT

                    events.append(DisappearanceEvent(
                        entity_id=entity_id,
                        entity_type=info["type"],
                        disappearance_index=idx,
                        previously_present_count=previously_present_count,
                        post_disappearance_absence_ratio=round(post_disappearance_absence_ratio, 3),
                        classification=classification
                    ))
                    # Only report first disappearance transition per sequence
                    break

        return events

    @staticmethod
    def _record_presence(occurrences: Dict[str, Any], entity_id: str, entity_type: str, index: int):
        if entity_id not in occurrences:
            occurrences[entity_id] = {
                "type": entity_type,
                "presence": []
            }
        while len(occurrences[entity_id]["presence"]) <= index:
            occurrences[entity_id]["presence"].append(False)
        occurrences[entity_id]["presence"][index] = True
