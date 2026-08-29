from datetime import datetime, timezone
from typing import Any, List, Callable
from src.prescription.trustworthiness.trustworthiness_schema import PrescriptionTrustworthinessProfile
from src.prescription.trustworthiness.reproducibility_engine import ReproducibilityEngine
from src.prescription.trustworthiness.perturbation_engine import PerturbationEngine
from src.prescription.trustworthiness.structural_robustness_analyzer import StructuralRobustnessAnalyzer
from src.prescription.trustworthiness.signal_robustness_analyzer import SignalRobustnessAnalyzer
from src.prescription.trustworthiness.cross_layer_consistency_engine import CrossLayerConsistencyEngine
from src.prescription.trustworthiness.provenance_completeness_analyzer import ProvenanceCompletenessAnalyzer
from src.prescription.trustworthiness.explanation_consistency_validator import ExplanationConsistencyValidator
from src.prescription.trustworthiness.trustworthiness_scoring_engine import TrustworthinessScoringEngine
from src.prescription.trustworthiness.trustworthiness_interpreter import TrustworthinessInterpreter

class TrustworthinessAggregator:
    @staticmethod
    def analyze_trustworthiness(
        baseline_meds: List[str],
        baseline_report: Any,
        structural_analysis: Any,
        evidence_intelligence: Any,
        contextual_stability: Any,
        explainability_profile: Any,
        analyze_func: Callable[[List[str]], Any]
    ) -> PrescriptionTrustworthinessProfile:
        """
        Orchestrates the entire Phase 12 computational evaluation pipeline.
        """
        meta = getattr(baseline_report, "metadata", None)
        if meta:
            analysis_id = getattr(meta, "analysis_id", "UNKNOWN_ANALYSIS")
            prescription_id = getattr(meta, "prescription_id", None) or analysis_id
        else:
            prescription_id = getattr(baseline_report, "prescription_id", "UNKNOWN_PRESCRIPTION")
            analysis_id = prescription_id

        # 1. Reproducibility Check (deterministic identical repeat execution)
        repeat_report = analyze_func(baseline_meds)
        reproducibility = ReproducibilityEngine.evaluate_reproducibility(
            baseline_report,
            [repeat_report]
        )

        # 2. Input Perturbation evaluation
        perturbations = PerturbationEngine.evaluate_perturbations(
            baseline_meds,
            baseline_report,
            analyze_func
        )

        # 3. Structural Robustness analyzer
        structure = StructuralRobustnessAnalyzer.analyze_robustness(
            structural_analysis,
            contextual_stability
        )

        # 4. Signal Robustness analyzer
        signals = SignalRobustnessAnalyzer.analyze_signals(
            evidence_intelligence,
            contextual_stability
        )

        # 5. Cross-Layer consistency
        consistency = CrossLayerConsistencyEngine.evaluate_consistency(
            structural_analysis,
            evidence_intelligence,
            contextual_stability,
            explainability_profile
        )

        # 6. Provenance Completeness evaluation
        provenance = ProvenanceCompletenessAnalyzer.analyze_provenance(explainability_profile)

        # 7. Explanation consistency validation
        explanation = ExplanationConsistencyValidator.validate_explanations(
            explainability_profile,
            getattr(baseline_report, "evidence_summary", None)
        )

        # 8. Compute scores
        overall_score, metrics, level = TrustworthinessScoringEngine.compute_trustworthiness(
            reproducibility,
            perturbations,
            structure,
            signals,
            consistency,
            provenance,
            explanation
        )

        # 9. Interpret narrative report
        narrative = TrustworthinessInterpreter.generate_narrative(
            overall_score,
            level,
            reproducibility,
            structure,
            consistency,
            provenance,
            explanation
        )

        return PrescriptionTrustworthinessProfile(
            prescription_id=prescription_id,
            analysis_id=analysis_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            reproducibility_profile=reproducibility,
            input_perturbation_results=perturbations,
            structural_robustness=structure,
            signal_robustness_profiles=signals,
            cross_layer_consistency=consistency,
            provenance_completeness=provenance,
            explanation_consistency=explanation,
            trustworthiness_metrics=metrics,
            overall_trustworthiness_level=level,
            executive_summary=narrative,
            guardrails=TrustworthinessInterpreter.get_guardrails()
        )
