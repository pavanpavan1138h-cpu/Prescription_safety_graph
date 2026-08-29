from typing import Dict, List, Any
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.intelligence.intelligence_schema import PrescriptionEvidenceIntelligenceProfile, ReinforcementLevel

class EvidenceIntelligenceValidator:
    @staticmethod
    def validate(
        profile: PrescriptionEvidenceIntelligenceProfile,
        report: PrescriptionSafetyReport
    ) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []

        canonical_ids = set(report.resolution_summary.canonical_drug_ids)
        report_pairs = {p.get("canonical_pair_key") for p in report.pair_results if p.get("canonical_pair_key")}
        # Add fallback format
        for p in report.pair_results:
            report_pairs.add(f"PAIR_{p['drug_a_id']}__{p['drug_b_id']}")

        # 1. Validate themes
        for theme in profile.themes:
            # Check participating drugs belong to prescription
            for did in theme.participating_drugs:
                if did not in canonical_ids:
                    errors.append(f"Theme {theme.theme_name} references drug '{did}' which is not in the prescription drugs list.")
            
            # Check supporting pairs belong to prescription
            for p_key in theme.supporting_pairs:
                if p_key not in report_pairs:
                    errors.append(f"Theme {theme.theme_name} references pair '{p_key}' which is not present in the evaluated pair list.")

        # 2. Validate signal groups
        for sg in profile.signal_groups:
            # Check score bounds
            if not (0.0 <= sg.reinforcement_score <= 1.0):
                errors.append(f"Signal group {sg.group_id} has out-of-bounds reinforcement score: {sg.reinforcement_score}.")

            # Check reinforcement level matches score
            score = sg.reinforcement_score
            level = sg.reinforcement_level
            if score >= 0.75 and level != ReinforcementLevel.STRONG_REINFORCEMENT:
                errors.append(f"Signal group {sg.group_id} score {score} doesn't match level {level}.")
            elif 0.50 <= score < 0.75 and level != ReinforcementLevel.MODERATE_REINFORCEMENT:
                errors.append(f"Signal group {sg.group_id} score {score} doesn't match level {level}.")
            elif 0.25 <= score < 0.50 and level != ReinforcementLevel.EMERGING_REINFORCEMENT:
                errors.append(f"Signal group {sg.group_id} score {score} doesn't match level {level}.")
            elif score < 0.25 and level != ReinforcementLevel.LIMITED_REINFORCEMENT:
                errors.append(f"Signal group {sg.group_id} score {score} doesn't match level {level}.")

            # Check participating drugs belong to prescription
            for did in sg.participating_drugs:
                if did not in canonical_ids:
                    errors.append(f"Signal group {sg.group_id} references drug '{did}' which is not in the prescription drugs list.")

            # Check supporting pairs belong to prescription
            for p_key in sg.supporting_pairs:
                if p_key not in report_pairs:
                    errors.append(f"Signal group {sg.group_id} references pair '{p_key}' which is not present in the evaluated pair list.")

        # 3. Validate concentration metrics
        cp = profile.concentration_profile
        if cp:
            if cp.dominant_drug_id and cp.dominant_drug_id not in canonical_ids:
                errors.append(f"Concentration profile references dominant drug '{cp.dominant_drug_id}' which is not in prescription.")
            if not (0.0 <= cp.edge_coverage_ratio <= 1.0):
                errors.append(f"Concentration profile edge coverage ratio out of bounds: {cp.edge_coverage_ratio}.")
            if not (0.0 <= cp.dominant_drug_share <= 1.0):
                errors.append(f"Concentration profile dominant drug share out of bounds: {cp.dominant_drug_share}.")
            if not (0.0 <= cp.dominant_cluster_edge_share <= 1.0):
                errors.append(f"Concentration profile dominant cluster share out of bounds: {cp.dominant_cluster_edge_share}.")

        # 4. Check safety warning presence in narrative
        if "CLINICAL GUARDRAIL NOTICE" not in profile.narrative:
            errors.append("Narrative report is missing the mandatory CLINICAL GUARDRAIL NOTICE section.")

        return {
            "validation_passed": len(errors) == 0,
            "error_count": len(errors),
            "errors": errors,
            "warning_count": len(warnings),
            "warnings": warnings
        }
