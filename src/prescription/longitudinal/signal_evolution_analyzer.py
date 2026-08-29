from typing import List, Dict
from src.prescription.longitudinal.longitudinal_schema import (
    SignalEvolutionProfile,
    SignalEvolutionLevel,
    EmergenceEvent,
    DisappearanceEvent
)
from src.prescription.longitudinal.snapshot_sequence_engine import NormalizedSnapshotView

class SignalEvolutionAnalyzer:
    @staticmethod
    def analyze_signals(
        views: List[NormalizedSnapshotView],
        emergence_events: List[EmergenceEvent],
        disappearance_events: List[DisappearanceEvent]
    ) -> List[SignalEvolutionProfile]:
        """
        Builds chronological sequences for each detected evidence theme.
        """
        profiles: List[SignalEvolutionProfile] = []
        total = len(views)
        if total < 2:
            return profiles

        # Get unique list of all themes seen across history
        all_themes = set()
        for v in views:
            all_themes.update(v.themes.keys())

        for theme in all_themes:
            presence_seq = []
            reinf_seq = []
            rank_seq = []
            present_count = 0

            for view in views:
                if theme in view.themes:
                    presence_seq.append(True)
                    reinf_seq.append(view.themes[theme]["reinforcement"])
                    rank_seq.append(view.themes[theme]["rank"])
                    present_count += 1
                else:
                    presence_seq.append(False)
                    reinf_seq.append(0.0)
                    rank_seq.append(999)

            persistence = present_count / total

            # Filters events belonging to current theme
            theme_emergences = [e for e in emergence_events if e.entity_id == theme]
            theme_disappearances = [d for d in disappearance_events if d.entity_id == theme]

            # Classification
            if persistence == 1.0:
                # Stable or strengthening check
                val_diff = reinf_seq[-1] - reinf_seq[0]
                if val_diff >= 0.15:
                    classification = SignalEvolutionLevel.SIGNAL_STRENGTHENING
                elif val_diff <= -0.15:
                    classification = SignalEvolutionLevel.SIGNAL_WEAKENING
                else:
                    classification = SignalEvolutionLevel.SIGNAL_STABLE
            elif len(theme_emergences) > 0 and len(theme_disappearances) > 0:
                classification = SignalEvolutionLevel.SIGNAL_VOLATILITY
            elif len(theme_emergences) > 0:
                classification = SignalEvolutionLevel.SIGNAL_RECONFIGURATION
            else:
                classification = SignalEvolutionLevel.SIGNAL_WEAKENING

            profiles.append(SignalEvolutionProfile(
                theme_id=theme,
                presence_sequence=presence_seq,
                reinforcement_sequence=[round(r, 3) for r in reinf_seq],
                rank_sequence=rank_seq,
                persistence_ratio=round(persistence, 3),
                emergence_events=theme_emergences,
                disappearance_events=theme_disappearances,
                classification=classification
            ))

        return sorted(profiles, key=lambda p: p.theme_id)
