from typing import Dict, Any, List
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.comparison.comparison_schema import PrescriptionComparativeIntelligenceProfile

class ComparisonValidator:
    @staticmethod
    def validate(
        profile: PrescriptionComparativeIntelligenceProfile,
        report_a: PrescriptionSafetyReport,
        report_b: PrescriptionSafetyReport
    ) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []

        drugs_a = set(report_a.resolution_summary.canonical_drug_ids)
        drugs_b = set(report_b.resolution_summary.canonical_drug_ids)

        meds = profile.medication_set_comparison

        # 1. Medication set accounting checks
        shared = set(meds.shared_drugs)
        a_only = set(meds.a_only_drugs)
        b_only = set(meds.b_only_drugs)

        if shared != drugs_a.intersection(drugs_b):
            errors.append("Shared drugs mismatch with intersection of A and B.")
        if a_only != drugs_a - drugs_b:
            errors.append("A-only drugs mismatch with drugs_a - drugs_b.")
        if b_only != drugs_b - drugs_a:
            errors.append("B-only drugs mismatch with drugs_b - drugs_a.")

        if len(shared) + len(a_only) != len(drugs_a):
            errors.append("Medication set A count check failed: shared + a_only != total_drugs_a.")
        if len(shared) + len(b_only) != len(drugs_b):
            errors.append("Medication set B count check failed: shared + b_only != total_drugs_b.")

        # 2. Structural metrics bounds checks
        st = profile.structural_delta
        if not (0.0 <= st.structural_delta_magnitude <= 1.0):
            errors.append(f"Structural delta magnitude out of bounds: {st.structural_delta_magnitude}")

        for rc in st.rank_comparisons:
            if rc.normalized_position_a is not None and not (0.0 <= rc.normalized_position_a <= 1.0):
                errors.append(f"Normalized position A out of bounds for drug {rc.drug_id}: {rc.normalized_position_a}")
            if rc.normalized_position_b is not None and not (0.0 <= rc.normalized_position_b <= 1.0):
                errors.append(f"Normalized position B out of bounds for drug {rc.drug_id}: {rc.normalized_position_b}")

        # 3. Stability metrics bounds
        stab = profile.stability_delta
        if not (-1.0 <= stab.stability_score_delta <= 1.0):
            errors.append(f"Stability score delta out of bounds: {stab.stability_score_delta}")
        if not (-1.0 <= stab.sensitivity_score_delta <= 1.0):
            errors.append(f"Sensitivity score delta out of bounds: {stab.sensitivity_score_delta}")

        # 4. Invariant traceability checks
        if profile.analysis_id_a != report_a.prescription_id:
            errors.append("Referenced Analysis A ID does not match Prescription Safety Report A ID.")
        if profile.analysis_id_b != report_b.prescription_id:
            errors.append("Referenced Analysis B ID does not match Prescription Safety Report B ID.")

        # 5. Guardrail check
        if "This comparison describes differences between computational evidence states" not in profile.narrative:
            errors.append("Narrative report is missing the mandatory CLINICAL SAFETY NOTICE warning.")

        # 6. Disallowed language check
        disallowed = ["safer than", "more dangerous", "should be removed", "should be added", "should be discontinued"]
        narrative_lower = profile.narrative.lower()
        for phrase in disallowed:
            if phrase in narrative_lower:
                errors.append(f"Narrative contains disallowed recommendation language: '{phrase}'.")

        return {
            "validation_passed": len(errors) == 0,
            "error_count": len(errors),
            "errors": errors,
            "warning_count": len(warnings),
            "warnings": warnings
        }
