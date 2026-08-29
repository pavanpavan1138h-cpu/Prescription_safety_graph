"""
src/prescription/structural/structural_interpretation_engine.py

Generates natural language structural interpretations and appends clinical warning guardrails.
"""

from typing import List, Optional
from src.prescription.structural.prescription_network_schema import (
    PrescriptionEvidenceNetwork,
    ClusterMetrics,
    DrugStructuralProfile,
    CounterfactualResult,
    TopologyClassification,
    StructuralInterpretation
)

class StructuralInterpretationEngine:
    @staticmethod
    def generate(
        network: PrescriptionEvidenceNetwork,
        topology: TopologyClassification,
        clusters: List[ClusterMetrics],
        profiles: List[DrugStructuralProfile],
        counterfactuals: List[CounterfactualResult]
    ) -> StructuralInterpretation:
        """
        Translates raw network metrics, cluster details, and counterfactual exclusions
        into a safe, structured clinical narrative summary.
        """
        highest_drug: Optional[str] = None
        highest_degree: int = 0
        
        if profiles:
            top_profile = profiles[0]
            if top_profile.evidence_degree > 0:
                highest_drug = top_profile.display_name
                highest_degree = top_profile.evidence_degree
                
        # 1. Connectivity narration
        active_clusters = [c for c in clusters if not c.is_isolated]
        isolated_drugs = [c for c in clusters if c.is_isolated]
        
        topology_desc = topology.primary_topology.value.replace("_", " ")
        secondary_desc = ", ".join([c.replace("_", " ") for c in topology.secondary_characteristics])
        
        conn_narrative = (
            f"The analyzed prescription evidence network is classified as having a primary '{topology_desc}' "
            f"topology with secondary characteristics: [{secondary_desc}]. "
            f"The network contains {len(active_clusters)} active connected cluster(s) of size > 1 and "
            f"{len(isolated_drugs)} structurally isolated drug(s) with no direct evidence edges."
        )
        
        # 2. Counterfactual impact narration
        impactful_exclusions = [cf for cf in counterfactuals if cf.contribution_level.value in ("HIGH_STRUCTURAL_IMPACT", "MODERATE_STRUCTURAL_IMPACT")]
        
        if impactful_exclusions:
            cf_list = []
            sorted_exclusions = sorted(impactful_exclusions, key=lambda x: x.structural_delta, reverse=True)[:3]
            for cf in sorted_exclusions:
                cf_list.append(f"{cf.display_name} ({cf.contribution_level.value.replace('_', ' ')} removing {cf.structural_delta} edge(s))")
            cf_narrative = (
                f"Computational exclusion analysis indicates that the structure of the evidence network is highly dependent "
                f"on the presence of: {'; '.join(cf_list)}."
            )
        else:
            cf_narrative = "Computational exclusion analysis indicates that no single drug removal has a high structural impact on the evidence network."
            
        return StructuralInterpretation(
            highest_participation_drug=highest_drug,
            highest_participation_degree=highest_degree,
            network_connectivity_narration=conn_narrative,
            counterfactual_impact_narration=cf_narrative
        )
