import math
from typing import List
from src.prescription.longitudinal.longitudinal_schema import (
    TrustworthinessEvolutionProfile,
    TrustworthinessEvolutionLevel
)
from src.prescription.longitudinal.snapshot_sequence_engine import NormalizedSnapshotView

class TrustworthinessEvolutionAnalyzer:
    @staticmethod
    def analyze_trustworthiness(
        views: List[NormalizedSnapshotView]
    ) -> TrustworthinessEvolutionProfile:
        """
        Monitors Phase 12 score progressions.
        """
        total = len(views)
        if total < 2:
            return TrustworthinessEvolutionProfile(
                score_sequence=[],
                level_sequence=[],
                score_delta_sequence=[],
                mean_score=1.0,
                score_volatility=0.0,
                classification=TrustworthinessEvolutionLevel.INSUFFICIENT_HISTORY
            )

        scores = [v.trust_score for v in views]
        levels = [v.trust_level for v in views]

        # Deltas
        deltas = []
        for i in range(1, total):
            deltas.append(scores[i] - scores[i - 1])

        mean_score = sum(scores) / total
        
        # Volatility (standard deviation)
        variance = sum((s - mean_score) ** 2 for s in scores) / total
        volatility = math.sqrt(variance)

        # Classification rules
        overall_delta = scores[-1] - scores[0]

        if volatility < 0.05:
            if mean_score >= 0.80:
                classification = TrustworthinessEvolutionLevel.CONSISTENTLY_HIGH
            else:
                classification = TrustworthinessEvolutionLevel.CONSISTENTLY_LIMITED
        elif overall_delta >= 0.08:
            classification = TrustworthinessEvolutionLevel.IMPROVING
        elif overall_delta <= -0.08:
            classification = TrustworthinessEvolutionLevel.DECLINING
        else:
            classification = TrustworthinessEvolutionLevel.VOLATILE

        return TrustworthinessEvolutionProfile(
            score_sequence=[round(s, 3) for s in scores],
            level_sequence=levels,
            score_delta_sequence=[round(d, 3) for d in deltas],
            mean_score=round(mean_score, 3),
            score_volatility=round(volatility, 3),
            classification=classification
        )
