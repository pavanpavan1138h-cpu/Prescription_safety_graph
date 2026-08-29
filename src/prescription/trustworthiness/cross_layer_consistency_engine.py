from typing import Any, List
from src.prescription.trustworthiness.trustworthiness_schema import (
    CrossLayerConsistencyProfile,
    CrossLayerConsistencyLevel
)

class CrossLayerConsistencyEngine:
    @staticmethod
    def evaluate_consistency(
        structural_analysis: Any,
        evidence_intelligence: Any,
        contextual_stability: Any,
        explainability_profile: Any
    ) -> CrossLayerConsistencyProfile:
        """
        Cross-examines overlapping top participants across Phase 8, 9, 10, and 11
        to determine converged hubs vs. multi-dimensional analysis distributions.
        """
        struct_dominant = []
        evidence_dominant = []
        dependency_dominant = []
        primary_contributors = []

        # 1. Phase 8 Hubs
        if structural_analysis:
            interp = getattr(structural_analysis, "structural_interpretation", None)
            if interp:
                highest = getattr(interp, "highest_participation_drug", None)
                if highest:
                    struct_dominant.append(highest)

        # 2. Phase 9 Evidence Dominant Drug
        if evidence_intelligence:
            conc = getattr(evidence_intelligence, "concentration_profile", None)
            if conc:
                dom_drug = getattr(conc, "dominant_drug_id", None)
                if dom_drug:
                    evidence_dominant.append(dom_drug)

        # 3. Phase 10 Contextual Dependencies
        if contextual_stability:
            deps = getattr(contextual_stability, "drug_dependencies", []) or []
            for d in deps:
                level = getattr(d, "dependency_level", "")
                d_id = getattr(d, "drug_id", "")
                if "CRITICAL" in level or "HIGH" in level:
                    if d_id:
                        dependency_dominant.append(d_id)

        # 4. Phase 11 Primary Contributors
        if explainability_profile:
            contribs = getattr(explainability_profile, "contribution_profiles", []) or []
            for c in contribs:
                level = getattr(c, "contribution_level", "")
                ent_id = getattr(c, "entity_id", "")
                ent_type = getattr(c, "entity_type", "")
                # We only match DRUG_ENTITY here to check cross-layer drug participation
                if "PRIMARY" in str(level) and "DRUG" in str(ent_type):
                    if ent_id:
                        primary_contributors.append(ent_id)

        # Calculate union of all lists, and the overlapping set
        all_sets = [set(struct_dominant), set(evidence_dominant), set(dependency_dominant), set(primary_contributors)]
        non_empty_sets = [s for s in all_sets if len(s) > 0]
        
        shared = []
        if len(non_empty_sets) >= 2:
            intersection = set.intersection(*non_empty_sets)
            shared = list(intersection)

        # Compute level
        if not non_empty_sets:
            level = CrossLayerConsistencyLevel.INSUFFICIENT_COMPARABLE_DATA
            explanation = "No dominant participants or contributors detected in the input layers to perform cross-layer matching."
        elif len(shared) > 0:
            level = CrossLayerConsistencyLevel.CONSISTENT_CONVERGENCE
            explanation = f"Consistent convergent hub detected: {', '.join(shared)} is identified across multiple analytical layers."
        else:
            # If there are participants but they don't overlap, it's multi-dimensional distribution
            level = CrossLayerConsistencyLevel.MULTI_DIMENSIONAL_ANALYTICAL_DISTRIBUTION
            explanation = "No single convergent drug hub. Analytical findings are distributed multi-dimensionally across structure, evidence, and stability."

        return CrossLayerConsistencyProfile(
            structural_dominant_participants=struct_dominant,
            evidence_dominant_participants=evidence_dominant,
            dependency_dominant_participants=dependency_dominant,
            primary_contributors=primary_contributors,
            shared_participants=shared,
            consistency_level=level,
            explanation=explanation
        )
