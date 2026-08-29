from typing import Dict, Any, List
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.contextual.contextual_schema import ContextualStabilityProfile, ScenarioType, InterpretationStabilityLevel

class ContextualStabilityValidator:
    @staticmethod
    def validate(
        profile: ContextualStabilityProfile,
        report: PrescriptionSafetyReport
    ) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []

        canonical_ids = set(report.resolution_summary.canonical_drug_ids)

        # 1. Scenarios Integrity
        has_baseline = False
        single_drug_scenarios_count = 0
        for s in profile.scenarios:
            if s.scenario_type == ScenarioType.BASELINE:
                has_baseline = True
                if len(s.included_drugs) != len(canonical_ids):
                    errors.append("Baseline scenario included drugs count does not match prescription canonical drugs count.")
            elif s.scenario_type == ScenarioType.SINGLE_DRUG_PERTURBATION:
                single_drug_scenarios_count += 1
                if len(s.excluded_drugs) != 1:
                    errors.append(f"Single-drug perturbation scenario {s.scenario_id} has excluded list size != 1.")
                ex_drug = s.excluded_drugs[0]
                if ex_drug not in canonical_ids:
                    errors.append(f"Single-drug scenario {s.scenario_id} excludes drug '{ex_drug}' which is not in prescription.")
            
            # Check surviving counts are non-negative
            if s.surviving_edges_count < 0:
                errors.append(f"Scenario {s.scenario_id} has negative surviving edges count: {s.surviving_edges_count}.")
            if s.surviving_convergent_edges_count < 0:
                errors.append(f"Scenario {s.scenario_id} has negative convergent surviving edges count: {s.surviving_convergent_edges_count}.")
            if s.surviving_themes_count < 0:
                errors.append(f"Scenario {s.scenario_id} has negative surviving themes count: {s.surviving_themes_count}.")

        if not has_baseline:
            errors.append("Missing SCENARIO_BASELINE context.")

        if len(canonical_ids) >= 2 and single_drug_scenarios_count != len(canonical_ids):
            errors.append(f"Expected {len(canonical_ids)} single-drug perturbation scenarios, but found {single_drug_scenarios_count}.")

        # 2. Metrics Boundedness
        es = profile.evidence_stability
        if not (0.0 <= es.overall_stability_score <= 1.0):
            errors.append(f"Evidence stability score out of bounds: {es.overall_stability_score}.")
        if not (0.0 <= es.pair_preservation_ratio <= 1.0):
            errors.append(f"Pair preservation ratio out of bounds: {es.pair_preservation_ratio}.")
        if not (0.0 <= es.convergent_preservation_ratio <= 1.0):
            errors.append(f"Convergent preservation ratio out of bounds: {es.convergent_preservation_ratio}.")
        if not (0.0 <= es.theme_preservation_ratio <= 1.0):
            errors.append(f"Theme preservation ratio out of bounds: {es.theme_preservation_ratio}.")
        if not (0.0 <= es.structural_edge_preservation_ratio <= 1.0):
            errors.append(f"Structural edge preservation ratio out of bounds: {es.structural_edge_preservation_ratio}.")

        cs = profile.context_sensitivity
        if not (0.0 <= cs.overall_sensitivity_score <= 1.0):
            errors.append(f"Context sensitivity score out of bounds: {cs.overall_sensitivity_score}.")
        if not (0.0 <= cs.status_change_rate <= 1.0):
            errors.append(f"Prescription status change rate out of bounds: {cs.status_change_rate}.")
        if not (0.0 <= cs.topology_change_rate <= 1.0):
            errors.append(f"Topology change rate out of bounds: {cs.topology_change_rate}.")
        if not (0.0 <= cs.theme_change_rate <= 1.0):
            errors.append(f"Dominant theme change rate out of bounds: {cs.theme_change_rate}.")

        for dep in profile.drug_dependencies:
            if not (0.0 <= dep.dependency_score <= 1.0):
                errors.append(f"Drug {dep.drug_id} dependency score out of bounds: {dep.dependency_score}.")
            if dep.drug_id not in canonical_ids:
                errors.append(f"Dependency impact references drug '{dep.drug_id}' which is not in prescription.")

        for sp in profile.signal_persistences:
            if not (0.0 <= sp.persistence_score <= 1.0):
                errors.append(f"Signal theme '{sp.theme_name}' persistence score out of bounds: {sp.persistence_score}.")

        # 3. Disclaimers checks
        if "This analysis computationally changes the graph context" not in profile.summary_narrative:
            errors.append("Contextual stability summary is missing the mandatory CLINICAL WARNING NOTICE disclaimer.")

        return {
            "validation_passed": len(errors) == 0,
            "error_count": len(errors),
            "errors": errors,
            "warning_count": len(warnings),
            "warnings": warnings
        }
