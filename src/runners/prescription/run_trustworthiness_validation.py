import logging
import json
from src.api.service import PrescriptionService
from src.prescription.trustworthiness.trustworthiness_validation import TrustworthinessValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_validation():
    logger.info("Initializing PrescriptionService for Phase 12 validation...")
    service = PrescriptionService()

    meds = ["cyclosporine", "fluconazole", "phentermine"]
    logger.info(f"Running Baseline Advanced Prescription Analysis for: {meds}")
    
    # 1. Trigger Advanced Analysis
    res = service.analyze_prescription_advanced(meds)
    analysis_id = res.prescription_report.metadata.analysis_id
    
    # 2. Extract Phase 12 Profile
    logger.info("Executing Phase 12 Trustworthiness Evaluation...")
    profile = service.get_trustworthiness_profile(analysis_id)
    
    assert profile is not None
    logger.info(f"Trustworthiness Profile generated successfully (Score: {profile.trustworthiness_metrics[0].value})")
    
    # 3. Assert invariants
    from src.prescription.trustworthiness.trustworthiness_schema import PrescriptionTrustworthinessProfile
    import dataclasses
    
    # Re-wrap Pydantic Schema values back into core dataclass structures for validate_invariants
    # First, reconstruct sub-dataclasses
    from src.prescription.trustworthiness.trustworthiness_schema import (
        ReproducibilityProfile, InputPerturbationResult, StructuralRobustnessProfile,
        SignalRobustnessProfile, CrossLayerConsistencyProfile, ProvenanceCompletenessProfile,
        ExplanationConsistencyProfile, TrustworthinessMetric, TrustworthinessLevel,
        ReproducibilityLevel, InputPerturbationType, PerturbationResultType,
        StructuralRobustnessLevel, SignalRobustnessLevel, CrossLayerConsistencyLevel
    )

    repro_dc = ReproducibilityProfile(
        baseline_signature=profile.reproducibility_profile.baseline_signature,
        repeat_run_signatures=profile.reproducibility_profile.repeat_run_signatures,
        deterministic_match_ratio=profile.reproducibility_profile.deterministic_match_ratio,
        classification=ReproducibilityLevel(profile.reproducibility_profile.classification),
        mismatched_components=profile.reproducibility_profile.mismatched_components
    )

    perts_dc = [
        InputPerturbationResult(
            perturbation_id=p.perturbation_id,
            perturbation_type=InputPerturbationType(p.perturbation_type),
            baseline_signature=p.baseline_signature,
            perturbed_signature=p.perturbed_signature,
            invariant_components=p.invariant_components,
            changed_components=p.changed_components,
            classification=PerturbationResultType(p.classification)
        ) for p in profile.input_perturbation_results
    ]

    struct_dc = StructuralRobustnessProfile(
        baseline_topology=profile.structural_robustness.baseline_topology,
        scenario_topology_distribution=profile.structural_robustness.scenario_topology_distribution,
        topology_persistence_ratio=profile.structural_robustness.topology_persistence_ratio,
        cluster_persistence_ratio=profile.structural_robustness.cluster_persistence_ratio,
        central_participant_persistence=profile.structural_robustness.central_participant_persistence,
        robustness_level=StructuralRobustnessLevel(profile.structural_robustness.robustness_level)
    )

    signals_dc = [
        SignalRobustnessProfile(
            theme_id=s.theme_id,
            baseline_present=s.baseline_present,
            scenario_presence_ratio=s.scenario_presence_ratio,
            reinforcement_stability=s.reinforcement_stability,
            classification=SignalRobustnessLevel(s.classification)
        ) for s in profile.signal_robustness_profiles
    ]

    consistency_dc = CrossLayerConsistencyProfile(
        structural_dominant_participants=profile.cross_layer_consistency.structural_dominant_participants,
        evidence_dominant_participants=profile.cross_layer_consistency.evidence_dominant_participants,
        dependency_dominant_participants=profile.cross_layer_consistency.dependency_dominant_participants,
        primary_contributors=profile.cross_layer_consistency.primary_contributors,
        shared_participants=profile.cross_layer_consistency.shared_participants,
        consistency_level=CrossLayerConsistencyLevel(profile.cross_layer_consistency.consistency_level),
        explanation=profile.cross_layer_consistency.explanation
    )

    provenance_dc = ProvenanceCompletenessProfile(
        traceability_coverage=profile.provenance_completeness.traceability_coverage,
        average_provenance_depth=profile.provenance_completeness.average_provenance_depth,
        orphaned_component_count=profile.provenance_completeness.orphaned_component_count,
        cross_layer_traceability=profile.provenance_completeness.cross_layer_traceability,
        completeness_level=profile.provenance_completeness.completeness_level
    )

    explanation_dc = ExplanationConsistencyProfile(
        claims_checked=profile.explanation_consistency.claims_checked,
        claims_supported=profile.explanation_consistency.claims_supported,
        unsupported_claims=profile.explanation_consistency.unsupported_claims,
        consistency_ratio=profile.explanation_consistency.consistency_ratio,
        classification=profile.explanation_consistency.classification
    )

    metrics_dc = [
        TrustworthinessMetric(
            metric_id=m.metric_id,
            metric_name=m.metric_name,
            value=m.value,
            normalized_value=m.normalized_value,
            classification=m.classification,
            description=m.description
        ) for m in profile.trustworthiness_metrics
    ]

    profile_dc = PrescriptionTrustworthinessProfile(
        prescription_id=profile.prescription_id,
        analysis_id=profile.analysis_id,
        generated_at=profile.generated_at,
        reproducibility_profile=repro_dc,
        input_perturbation_results=perts_dc,
        structural_robustness=struct_dc,
        signal_robustness_profiles=signals_dc,
        cross_layer_consistency=consistency_dc,
        provenance_completeness=provenance_dc,
        explanation_consistency=explanation_dc,
        trustworthiness_metrics=metrics_dc,
        overall_trustworthiness_level=TrustworthinessLevel(profile.overall_trustworthiness_level),
        executive_summary=profile.executive_summary,
        guardrails=profile.guardrails
    )

    val_res = TrustworthinessValidator.validate_invariants(profile_dc)
    print(json.dumps(val_res, indent=2))
    
    assert val_res["validation_passed"] is True
    print("\nSUCCESS: Phase 12 trustworthiness engine validated successfully!")

if __name__ == "__main__":
    run_validation()
