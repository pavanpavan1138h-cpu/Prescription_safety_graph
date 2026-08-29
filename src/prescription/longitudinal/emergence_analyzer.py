from typing import List, Dict, Any
from src.prescription.longitudinal.longitudinal_schema import (
    EmergenceEvent,
    EmergenceClassification
)
from src.prescription.longitudinal.snapshot_sequence_engine import NormalizedSnapshotView

class EmergenceAnalyzer:
    @staticmethod
    def analyze_emergence(
        views: List[NormalizedSnapshotView]
    ) -> List[EmergenceEvent]:
        """
        Scans sequence to identify when drugs or themes emerge.
        """
        events: List[EmergenceEvent] = []
        total = len(views)
        if total < 2:
            return events

        # Helper structure to trace emergence events per entity
        entity_occurrences: Dict[str, Dict[str, Any]] = {}

        # Scan for medications emergence
        for idx, view in enumerate(views):
            for med in view.medications:
                EmergenceAnalyzer._record_presence(entity_occurrences, med, "DRUG", idx)

        # Scan for themes emergence
        for idx, view in enumerate(views):
            for theme_id in view.themes.keys():
                EmergenceAnalyzer._record_presence(entity_occurrences, theme_id, "EVIDENCE_THEME", idx)

        # Evaluate classifications
        for entity_id, info in entity_occurrences.items():
            presence = info["presence"]
            
            # Find first emergence transition (absent -> present)
            for idx in range(1, total):
                if not presence[idx - 1] and presence[idx]:
                    # Emergence detected at idx!
                    # Calculate stats:
                    previously_absent_count = sum(1 for p in presence[:idx] if not p)
                    post_emergence_snapshots = presence[idx:]
                    post_emergence_persistence = sum(1 for p in post_emergence_snapshots if p) / len(post_emergence_snapshots)

                    # Determine classification based on behavior post-emergence
                    if len(post_emergence_snapshots) == 1:
                        classification = EmergenceClassification.NEWLY_EMERGED
                    elif post_emergence_persistence >= 0.80:
                        classification = EmergenceClassification.PERSISTENTLY_EMERGED
                    elif post_emergence_persistence <= 0.35:
                        classification = EmergenceClassification.TRANSIENTLY_EMERGED
                    else:
                        classification = EmergenceClassification.RECURRENTLY_EMERGED

                    events.append(EmergenceEvent(
                        entity_id=entity_id,
                        entity_type=info["type"],
                        emergence_index=idx,
                        previously_absent_count=previously_absent_count,
                        post_emergence_persistence=round(post_emergence_persistence, 3),
                        classification=classification
                    ))
                    # Only report first emergence transition per sequence
                    break

        return events

    @staticmethod
    def _record_presence(occurrences: Dict[str, Any], entity_id: str, entity_type: str, index: int):
        if entity_id not in occurrences:
            # We initialize with a list of False values for each step in history
            # The list size is dynamically managed by index, but we assume we know the total index bounds or just initialize on-demand.
            occurrences[entity_id] = {
                "type": entity_type,
                "presence": []
            }
        # Expand list size to index + 1
        while len(occurrences[entity_id]["presence"]) <= index:
            occurrences[entity_id]["presence"].append(False)
        occurrences[entity_id]["presence"][index] = True
