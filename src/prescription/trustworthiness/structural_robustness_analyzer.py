from typing import Any, Optional, Dict
from src.prescription.trustworthiness.trustworthiness_schema import (
    StructuralRobustnessProfile,
    StructuralRobustnessLevel
)

class StructuralRobustnessAnalyzer:
    @staticmethod
    def analyze_robustness(
        structural_analysis: Any,
        contextual_stability: Any
    ) -> StructuralRobustnessProfile:
        """
        Reuses Phase 8 and Phase 10 outputs to evaluate structural stability metrics.
        """
        if not structural_analysis:
            return StructuralRobustnessProfile(
                baseline_topology="UNKNOWN",
                scenario_topology_distribution={},
                topology_persistence_ratio=0.0,
                cluster_persistence_ratio=0.0,
                central_participant_persistence=0.0,
                robustness_level=StructuralRobustnessLevel.INSUFFICIENT_STRUCTURAL_CONTEXT
            )

        # Baseline topology from topology or structural_interpretation fallback
        top_obj = getattr(structural_analysis, "topology", None)
        baseline_top = "UNKNOWN"
        if top_obj:
            baseline_top = getattr(top_obj, "primary_topology", "UNKNOWN")
        else:
            interpretation = getattr(structural_analysis, "structural_interpretation", None)
            if interpretation:
                baseline_top = getattr(interpretation, "topology_classification", "UNKNOWN")

        # Distribution of topologies across scenarios in Phase 10
        topo_dist: Dict[str, int] = {}
        scenarios = getattr(contextual_stability, "scenarios", []) or []
        
        for s in scenarios:
            t_class = getattr(s, "topology_classification", None)
            if t_class:
                topo_dist[t_class] = topo_dist.get(t_class, 0) + 1

        total_scenarios = len(scenarios)
        if total_scenarios > 0:
            matching_topo = topo_dist.get(baseline_top, 0)
            topo_persistence = matching_topo / total_scenarios
        else:
            topo_persistence = 1.0

        # Cluster preservation ratio from evidence_stability
        ev_stability = getattr(contextual_stability, "evidence_stability", None)
        if ev_stability:
            cluster_persistence = getattr(ev_stability, "structural_edge_preservation_ratio", 1.0)
            pair_preservation = getattr(ev_stability, "pair_preservation_ratio", 1.0)
        else:
            cluster_persistence = 1.0
            pair_preservation = 1.0

        # Calculate central participant persistence
        central_persistence = 1.0
        interpretation = getattr(structural_analysis, "structural_interpretation", None)
        if interpretation and scenarios:
            baseline_hub = getattr(interpretation, "highest_participation_drug", None)
            if baseline_hub:
                # Count how often the baseline hub survives in the scenarios' included_drugs
                survived_count = 0
                scenarios_with_hub = 0
                for s in scenarios:
                    inc_drugs = getattr(s, "included_drugs", []) or []
                    exc_drugs = getattr(s, "excluded_drugs", []) or []
                    if baseline_hub in inc_drugs or baseline_hub not in exc_drugs:
                        scenarios_with_hub += 1
                        # If topology or dominant theme indicates structure survived
                        if getattr(s, "topology_classification", "") == baseline_top:
                            survived_count += 1
                if scenarios_with_hub > 0:
                    central_persistence = survived_count / scenarios_with_hub

        # Overall average structural score
        overall_score = (topo_persistence + cluster_persistence + central_persistence) / 3.0

        if overall_score >= 0.80:
            level = StructuralRobustnessLevel.HIGHLY_ROBUST_STRUCTURE
        elif overall_score >= 0.60:
            level = StructuralRobustnessLevel.ROBUST_STRUCTURE
        elif overall_score >= 0.40:
            level = StructuralRobustnessLevel.MODERATELY_SENSITIVE_STRUCTURE
        else:
            level = StructuralRobustnessLevel.FRAGILE_STRUCTURE

        return StructuralRobustnessProfile(
            baseline_topology=baseline_top,
            scenario_topology_distribution=topo_dist,
            topology_persistence_ratio=round(topo_persistence, 3),
            cluster_persistence_ratio=round(cluster_persistence, 3),
            central_participant_persistence=round(central_persistence, 3),
            robustness_level=level
        )
