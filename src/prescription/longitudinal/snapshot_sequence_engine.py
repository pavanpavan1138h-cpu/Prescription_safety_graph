from typing import Any, Dict, List
from src.prescription.longitudinal.longitudinal_schema import PrescriptionSnapshotReference

class NormalizedSnapshotView:
    def __init__(self, ref: PrescriptionSnapshotReference):
        self.sequence_index = ref.sequence_index
        self.analysis_id = ref.analysis_id
        self.prescription_id = ref.prescription_id
        
        # Load backing snapshot
        snap = getattr(ref, "_snapshot", None)
        
        # 1. Meds
        self.medications = ref.medications
        
        # 2. Structure
        self.topology = "UNKNOWN_TOPOLOGY"
        self.central_participants: List[str] = []
        self.cluster_count = 0
        self.density = 0.0

        struct = getattr(snap, "structural_analysis", None)
        if struct:
            # Topology
            if hasattr(struct, "topology") and struct.topology:
                self.topology = getattr(struct.topology, "primary_topology", "UNKNOWN_TOPOLOGY")
            elif hasattr(struct, "structural_interpretation") and struct.structural_interpretation:
                self.topology = getattr(struct.structural_interpretation, "topology_classification", "UNKNOWN_TOPOLOGY")
            
            # Central participants
            rankings = getattr(struct, "centrality_rankings", []) or []
            self.central_participants = [getattr(r, "drug_id", "") for r in rankings if hasattr(r, "drug_id")]
            
            # Clusters
            self.cluster_count = len(getattr(struct, "evidence_clusters", []) or [])
            # Density
            metrics = getattr(struct, "network_metrics", None)
            if metrics:
                self.density = getattr(metrics, "density", 0.0)

        # 3. Signals
        self.themes: Dict[str, Dict[str, Any]] = {}
        intel = getattr(snap, "evidence_intelligence", None)
        if intel:
            themes_list = getattr(intel, "signal_themes", []) or []
            for theme in themes_list:
                theme_id = getattr(theme, "theme_id", "")
                if theme_id:
                    self.themes[theme_id] = {
                        "present": True,
                        "reinforcement": getattr(theme, "reinforcement_ratio", 1.0),
                        "rank": getattr(theme, "significance_rank", 99)
                    }

        # 4. Stability
        self.stability = "CONSISTENTLY_STABLE"
        self.sensitivity = 0.0
        contextual = getattr(snap, "contextual_stability", None)
        if contextual:
            self.stability = getattr(contextual, "interpretation_stability", "CONSISTENTLY_STABLE")
            if hasattr(self.stability, "value"):
                self.stability = self.stability.value
            
            # Sensitivity estimation (from variance or scenario count)
            scenarios = getattr(contextual, "perturbation_scenarios", []) or []
            if scenarios:
                total_scens = len(scenarios)
                deviations = sum(1 for s in scenarios if getattr(s, "outcome_diverged", False))
                self.sensitivity = deviations / max(total_scens, 1)

        # 5. Trustworthiness
        self.trust_score = 1.0
        self.trust_level = "HIGH_COMPUTATIONAL_TRUSTWORTHINESS"
        trust = getattr(snap, "trustworthiness", None)
        if trust:
            self.trust_score = getattr(trust, "overall_trustworthiness_level", 1.0)
            if not isinstance(self.trust_score, float):
                # Try finding metric or fallback
                metrics = getattr(trust, "trustworthiness_metrics", []) or []
                if metrics:
                    self.trust_score = sum(getattr(m, "normalized_value", 1.0) for m in metrics) / len(metrics)
                else:
                    self.trust_score = 1.0
            
            self.trust_level = getattr(trust, "overall_trustworthiness_level", "HIGH_COMPUTATIONAL_TRUSTWORTHINESS")
            if hasattr(self.trust_level, "value"):
                self.trust_level = self.trust_level.value

        # 6. Explainability / Contributors & Provenance
        self.primary_contributors: List[str] = []
        self.traceability_coverage = 1.0
        
        explainability = getattr(snap, "explainability", None)
        if explainability:
            # Primary contributors
            conts = getattr(explainability, "contribution_profiles", []) or []
            self.primary_contributors = [getattr(c, "entity_id", "") for c in conts if hasattr(c, "entity_id")]
            
            # Traceability coverage
            trace = getattr(explainability, "traceability_profile", None)
            if trace:
                self.traceability_coverage = getattr(trace, "traceability_coverage_score", 1.0)


class SnapshotSequenceEngine:
    @staticmethod
    def normalize_sequence(
        timeline: List[PrescriptionSnapshotReference]
    ) -> List[NormalizedSnapshotView]:
        """
        Translates raw snapshot object sequences into clean NormalizedSnapshotView lists.
        """
        return [NormalizedSnapshotView(ref) for ref in timeline]
