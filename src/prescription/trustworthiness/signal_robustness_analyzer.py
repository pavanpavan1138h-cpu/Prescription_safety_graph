from typing import Any, List
from src.prescription.trustworthiness.trustworthiness_schema import (
    SignalRobustnessProfile,
    SignalRobustnessLevel
)

class SignalRobustnessAnalyzer:
    @staticmethod
    def analyze_signals(
        evidence_intelligence: Any,
        contextual_stability: Any
    ) -> List[SignalRobustnessProfile]:
        """
        Evaluates evidence signal stability by mapping theme presence across removal scenarios.
        """
        profiles: List[SignalRobustnessProfile] = []
        if not evidence_intelligence or not hasattr(evidence_intelligence, "themes"):
            return []

        themes = getattr(evidence_intelligence, "themes", []) or []
        persistences = getattr(contextual_stability, "signal_persistences", []) or []
        
        # Build map of signal persistences from contextual stability (Phase 10)
        persistence_map = {}
        for p in persistences:
            name = getattr(p, "theme_name", "")
            score = getattr(p, "persistence_score", 1.0)
            persistence_map[name] = score

        for theme in themes:
            theme_name = getattr(theme, "theme_name", "")
            theme_id = getattr(theme, "theme_id", theme_name)
            
            # Retrieve or compute scenario presence ratio
            ratio = persistence_map.get(theme_name, 1.0)
            stability = ratio  # Falls back to simple persistence for stability

            if ratio >= 0.80:
                level = SignalRobustnessLevel.HIGHLY_ROBUST_SIGNAL
            elif ratio >= 0.60:
                level = SignalRobustnessLevel.ROBUST_SIGNAL
            elif ratio >= 0.40:
                level = SignalRobustnessLevel.MODERATELY_SENSITIVE_SIGNAL
            elif ratio >= 0.20:
                level = SignalRobustnessLevel.FRAGILE_SIGNAL
            else:
                level = SignalRobustnessLevel.NON_PERSISTENT_SIGNAL

            profiles.append(SignalRobustnessProfile(
                theme_id=theme_id,
                baseline_present=True,
                scenario_presence_ratio=round(ratio, 3),
                reinforcement_stability=round(stability, 3),
                classification=level
            ))

        return profiles
