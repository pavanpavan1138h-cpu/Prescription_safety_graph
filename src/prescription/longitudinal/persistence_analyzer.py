from typing import List, Dict, Any
from src.prescription.longitudinal.longitudinal_schema import (
    PersistenceProfile,
    PersistenceLevel
)
from src.prescription.longitudinal.snapshot_sequence_engine import NormalizedSnapshotView

class PersistenceAnalyzer:
    @staticmethod
    def analyze_persistence(
        views: List[NormalizedSnapshotView]
    ) -> List[PersistenceProfile]:
        """
        Calculates presence ratios, runs, and levels for drugs and evidence themes.
        """
        profiles: List[PersistenceProfile] = []
        total = len(views)
        if total == 0:
            return profiles

        # 1. Meds persistence tracking
        med_history: Dict[str, List[bool]] = {}
        med_first: Dict[str, int] = {}
        med_last: Dict[str, int] = {}
        
        for idx, view in enumerate(views):
            for med in view.medications:
                if med not in med_history:
                    med_history[med] = [False] * total
                    med_first[med] = idx
                med_history[med][idx] = True
                med_last[med] = idx

        for med, hist in med_history.items():
            profiles.append(
                PersistenceAnalyzer._build_profile(
                    entity_id=med,
                    entity_type="DRUG",
                    history=hist,
                    first_idx=med_first[med],
                    last_idx=med_last[med]
                )
            )

        # 2. Evidence Themes persistence tracking
        theme_history: Dict[str, List[bool]] = {}
        theme_first: Dict[str, int] = {}
        theme_last: Dict[str, int] = {}

        for idx, view in enumerate(views):
            for theme_id in view.themes.keys():
                if theme_id not in theme_history:
                    theme_history[theme_id] = [False] * total
                    theme_first[theme_id] = idx
                theme_history[theme_id][idx] = True
                theme_last[theme_id] = idx

        for theme, hist in theme_history.items():
            profiles.append(
                PersistenceAnalyzer._build_profile(
                    entity_id=theme,
                    entity_type="EVIDENCE_THEME",
                    history=hist,
                    first_idx=theme_first[theme],
                    last_idx=theme_last[theme]
                )
            )

        return profiles

    @staticmethod
    def _build_profile(
        entity_id: str,
        entity_type: str,
        history: List[bool],
        first_idx: int,
        last_idx: int
    ) -> PersistenceProfile:
        total = len(history)
        present_count = sum(1 for p in history if p)
        ratio = present_count / total

        # Longest consecutive run
        max_run = 0
        current_run = 0
        for present in history:
            if present:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0

        # Classification mapping rules
        if total < 2:
            level = PersistenceLevel.INSUFFICIENT_HISTORY
        elif ratio >= 0.80:
            level = PersistenceLevel.HIGHLY_PERSISTENT
        elif ratio >= 0.60:
            level = PersistenceLevel.PERSISTENT
        elif ratio >= 0.40:
            level = PersistenceLevel.MODERATELY_PERSISTENT
        elif ratio >= 0.20:
            level = PersistenceLevel.INTERMITTENT
        else:
            level = PersistenceLevel.NON_PERSISTENT

        return PersistenceProfile(
            entity_id=entity_id,
            entity_type=entity_type,
            presence_ratio=round(ratio, 3),
            longest_consecutive_run=max_run,
            first_seen_index=first_idx,
            last_seen_index=last_idx,
            persistence_level=level
        )
