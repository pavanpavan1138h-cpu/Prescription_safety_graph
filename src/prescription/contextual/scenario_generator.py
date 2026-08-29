from typing import List, Any
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.contextual.contextual_schema import ScenarioContext, ScenarioType

class ScenarioGenerator:
    @staticmethod
    def generate_all(
        report: PrescriptionSafetyReport,
        structural_analysis: Any
    ) -> List[ScenarioContext]:
        canonical_ids = report.resolution_summary.canonical_drug_ids
        analysis_id = report.prescription_id
        
        scenarios: List[ScenarioContext] = []

        # 1. Baseline Scenario
        scenarios.append(ScenarioContext(
            scenario_id="SCENARIO_BASELINE",
            scenario_type=ScenarioType.BASELINE,
            baseline_analysis_id=analysis_id,
            included_drugs=canonical_ids,
            excluded_drugs=[]
        ))

        # 2. Single-Drug Perturbations
        # Only if we have at least 2 drugs (perturbation is empty/meaningless for 1 drug)
        if len(canonical_ids) >= 2:
            for drug_id in canonical_ids:
                scenarios.append(ScenarioContext(
                    scenario_id=f"SCENARIO_EXCLUDE_{drug_id}",
                    scenario_type=ScenarioType.SINGLE_DRUG_PERTURBATION,
                    baseline_analysis_id=analysis_id,
                    included_drugs=[d for d in canonical_ids if d != drug_id],
                    excluded_drugs=[drug_id]
                ))

        # 3. Cluster Perturbations
        if structural_analysis and hasattr(structural_analysis, "clusters") and hasattr(structural_analysis, "drug_structural_profiles"):
            active_clusters = [c for c in structural_analysis.clusters if not c.is_isolated]
            for cluster in active_clusters:
                # Find all drugs belonging to this cluster
                cluster_members = [
                    p.drug_id for p in structural_analysis.drug_structural_profiles
                    if p.cluster_id == cluster.cluster_id
                ]
                
                # Only perturb if the cluster doesn't contain all drugs (would leave 0 drugs)
                # and contains at least 1 drug.
                if 0 < len(cluster_members) < len(canonical_ids):
                    scenarios.append(ScenarioContext(
                        scenario_id=f"SCENARIO_EXCLUDE_CLUSTER_{cluster.cluster_id}",
                        scenario_type=ScenarioType.CLUSTER_CONTEXT,
                        baseline_analysis_id=analysis_id,
                        included_drugs=[d for d in canonical_ids if d not in cluster_members],
                        excluded_drugs=cluster_members,
                        included_clusters=[c.cluster_id for c in active_clusters if c.cluster_id != cluster.cluster_id],
                        excluded_clusters=[cluster.cluster_id]
                    ))

        return scenarios
