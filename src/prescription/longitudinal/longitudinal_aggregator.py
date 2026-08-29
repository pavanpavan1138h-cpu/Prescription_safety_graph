from typing import List, Any
from src.prescription.longitudinal.longitudinal_schema import (
    PrescriptionLongitudinalProfile,
    LongitudinalEvolutionLevel
)
from src.prescription.longitudinal.timeline_resolver import TimelineResolver
from src.prescription.longitudinal.snapshot_sequence_engine import SnapshotSequenceEngine
from src.prescription.longitudinal.persistence_analyzer import PersistenceAnalyzer
from src.prescription.longitudinal.emergence_analyzer import EmergenceAnalyzer
from src.prescription.longitudinal.disappearance_analyzer import DisappearanceAnalyzer
from src.prescription.longitudinal.change_point_detector import ChangePointDetector
from src.prescription.longitudinal.structural_evolution_analyzer import StructuralEvolutionAnalyzer
from src.prescription.longitudinal.signal_evolution_analyzer import SignalEvolutionAnalyzer
from src.prescription.longitudinal.stability_evolution_analyzer import StabilityEvolutionAnalyzer
from src.prescription.longitudinal.trustworthiness_evolution_analyzer import TrustworthinessEvolutionAnalyzer
from src.prescription.longitudinal.cross_layer_evolution_engine import CrossLayerEvolutionEngine
from src.prescription.longitudinal.longitudinal_interpreter import LongitudinalInterpreter

class LongitudinalAggregator:
    @staticmethod
    def aggregate_longitudinal_profile(
        snapshots: List[Any]
    ) -> PrescriptionLongitudinalProfile:
        """
        Orchestrates the Phase 13 evolution tracking pipeline.
        """
        # 1. Timeline resolution
        timeline = TimelineResolver.resolve_timeline(snapshots)

        # 2. Normalization views
        views = SnapshotSequenceEngine.normalize_sequence(timeline)

        # 3. Core analyzers
        persistence = PersistenceAnalyzer.analyze_persistence(views)
        emergence = EmergenceAnalyzer.analyze_emergence(views)
        disappearance = DisappearanceAnalyzer.analyze_disappearance(views)
        change_points = ChangePointDetector.detect_change_points(views)

        # 4. Evolution tracks
        structure = StructuralEvolutionAnalyzer.analyze_structure(views, change_points)
        signals = SignalEvolutionAnalyzer.analyze_signals(views, emergence, disappearance)
        stability = StabilityEvolutionAnalyzer.analyze_stability(views)
        trustworthiness = TrustworthinessEvolutionAnalyzer.analyze_trustworthiness(views)
        cross_layer = CrossLayerEvolutionEngine.analyze_cross_layer(views, change_points)

        # 5. Determine overall level
        total = len(views)
        if total < 2:
            overall_level = LongitudinalEvolutionLevel.INSUFFICIENT_LONGITUDINAL_CONTEXT
        else:
            major_cps = sum(1 for cp in change_points if cp.aggregate_change_score >= 0.60)
            if major_cps >= 2:
                overall_level = LongitudinalEvolutionLevel.HIGH_ANALYTICAL_VOLATILITY
            elif major_cps == 1:
                overall_level = LongitudinalEvolutionLevel.MAJOR_ANALYTICAL_TRANSITION
            elif len(change_points) > 0:
                overall_level = LongitudinalEvolutionLevel.GRADUAL_EVOLUTION
            else:
                overall_level = LongitudinalEvolutionLevel.HIGH_CONTINUITY

        # 6. Generate narrative
        narrative = LongitudinalInterpreter.generate_narrative(
            snapshots_count=total,
            overall_level=overall_level,
            change_point_count=len(change_points),
            structure=structure,
            stability=stability,
            trustworthiness=trustworthiness
        )

        return PrescriptionLongitudinalProfile(
            timeline=timeline,
            persistence_profiles=persistence,
            emergence_events=emergence,
            disappearance_events=disappearance,
            change_points=change_points,
            structural_evolution=structure,
            signal_evolution=signals,
            stability_evolution=stability,
            trustworthiness_evolution=trustworthiness,
            cross_layer_evolution=cross_layer,
            overall_evolution_level=overall_level,
            longitudinal_summary=narrative,
            guardrails=LongitudinalInterpreter.get_guardrails()
        )
