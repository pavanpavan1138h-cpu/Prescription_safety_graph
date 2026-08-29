from typing import Any
from src.prescription.trustworthiness.trustworthiness_schema import ProvenanceCompletenessProfile

class ProvenanceCompletenessAnalyzer:
    @staticmethod
    def analyze_provenance(explainability_profile: Any) -> ProvenanceCompletenessProfile:
        """
        Reuses Phase 11 explainability traceability profiles to evaluate completeness.
        """
        if not explainability_profile:
            return ProvenanceCompletenessProfile(
                traceability_coverage=0.0,
                average_provenance_depth=0.0,
                orphaned_component_count=0,
                cross_layer_traceability="NONE",
                completeness_level="INSUFFICIENT_PROVENANCE_COMPLETENESS"
            )

        trace = getattr(explainability_profile, "traceability_profile", None)
        if not trace:
            return ProvenanceCompletenessProfile(
                traceability_coverage=0.0,
                average_provenance_depth=0.0,
                orphaned_component_count=0,
                cross_layer_traceability="NONE",
                completeness_level="INSUFFICIENT_PROVENANCE_COMPLETENESS"
            )

        coverage = getattr(trace, "traceability_coverage_score", 0.0)
        depth = getattr(trace, "average_provenance_depth", 0.0)
        orphaned = getattr(trace, "orphaned_components_count", 0)
        cl_trace = getattr(trace, "cross_layer_traceability", "NONE")
        cl_trace_val = cl_trace.value if hasattr(cl_trace, "value") else str(cl_trace)

        # Completeness scoring rule
        if coverage >= 0.85 and orphaned == 0:
            level = "HIGH_PROVENANCE_COMPLETENESS"
        elif coverage >= 0.60:
            level = "MODERATE_PROVENANCE_COMPLETENESS"
        elif coverage >= 0.30:
            level = "LIMITED_PROVENANCE_COMPLETENESS"
        else:
            level = "INSUFFICIENT_PROVENANCE_COMPLETENESS"

        return ProvenanceCompletenessProfile(
            traceability_coverage=round(coverage, 3),
            average_provenance_depth=round(depth, 3),
            orphaned_component_count=orphaned,
            cross_layer_traceability=cl_trace_val,
            completeness_level=level
        )
