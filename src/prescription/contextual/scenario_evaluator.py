from typing import Any, List, Dict, Tuple
from src.prescription.schemas import PrescriptionSafetyReport, PrescriptionResolutionResult, ResolvedPrescriptionDrug, ResolutionStatus
from src.prescription.aggregation import PrescriptionAggregator
from src.reasoning.schemas import EvidenceStatus
from src.prescription.structural.prescription_structural_analyzer import PrescriptionStructuralAnalyzer
from src.prescription.intelligence.intelligence_aggregator import PrescriptionEvidenceIntelligenceAnalyzer
from src.prescription.contextual.contextual_schema import ScenarioContext, ScenarioProfile, ScenarioType

class MockSafetyInferenceResult:
    def __init__(self, evidence_status: EvidenceStatus, drug_a_id: str, drug_b_id: str):
        self.evidence_status = evidence_status
        self.drug_a_id = drug_a_id
        self.drug_b_id = drug_b_id

class ScenarioEvaluator:
    @staticmethod
    def evaluate(
        context: ScenarioContext,
        baseline_report: PrescriptionSafetyReport,
        reasoner: Any
    ) -> Tuple[ScenarioProfile, Any, Any]:
        included_drugs = context.included_drugs
        excluded_drugs = context.excluded_drugs
        
        # 1. Filter resolution summary
        # Keep resolved drugs that belong to included_drugs
        filtered_resolved_drugs = [
            d for d in baseline_report.resolution_summary.resolved_drugs
            if d.resolved_internal_drug_id in included_drugs
        ]
        
        filtered_res_summary = PrescriptionResolutionResult(
            original_inputs=included_drugs,
            resolved_drugs=filtered_resolved_drugs,
            canonical_drug_ids=included_drugs,
            unresolved_inputs=[],
            ambiguous_inputs=[],
            duplicate_inputs=[]
        )

        # 2. Filter pair results and prioritize findings
        filtered_pair_results = [
            p for p in baseline_report.pair_results
            if p["drug_a_id"] in included_drugs and p["drug_b_id"] in included_drugs
        ]

        filtered_prioritized_findings = [
            f for f in baseline_report.prioritized_findings
            if f.drug_a_id in included_drugs and f.drug_b_id in included_drugs
        ]

        # 3. Reconstruct Mock pair inferences for the aggregator
        # Let's map evidence status string to Enum
        pair_inferences = []
        drug_name_map = {}
        for d in filtered_resolved_drugs:
            if d.resolved_internal_drug_id and d.display_name:
                drug_name_map[d.resolved_internal_drug_id] = d.display_name

        for p in filtered_pair_results:
            st_str = p.get("evidence_status", "NO_DIRECT_GRAPH_EVIDENCE")
            # Map string to Enum value
            try:
                st_enum = EvidenceStatus(st_str)
            except ValueError:
                st_enum = EvidenceStatus.NO_DIRECT_GRAPH_EVIDENCE
                
            mock_res = MockSafetyInferenceResult(
                evidence_status=st_enum,
                drug_a_id=p["drug_a_id"],
                drug_b_id=p["drug_b_id"]
            )
            pair_inferences.append((p.get("pair_index", 0), mock_res, p["drug_a_name"], p["drug_b_name"]))

        # Re-run prescription aggregation
        filtered_ev_summary, filtered_drug_participation = PrescriptionAggregator.aggregate_evidence(
            res_summary=filtered_res_summary,
            pair_inferences=pair_inferences,
            drug_name_map=drug_name_map
        )

        # 4. Construct filtered PrescriptionSafetyReport object
        filtered_report = PrescriptionSafetyReport(
            prescription_id=baseline_report.prescription_id,
            generated_at=baseline_report.generated_at,
            resolution_summary=filtered_res_summary,
            evidence_summary=filtered_ev_summary,
            drug_participation=filtered_drug_participation,
            prioritized_findings=filtered_prioritized_findings,
            pair_results=filtered_pair_results,
            clinical_narrative_report=""
        )

        # 5. Execute Phase 8 structural analysis and Phase 9 intelligence aggregator
        struct_analysis = PrescriptionStructuralAnalyzer.analyze(filtered_report)
        intel_profile = PrescriptionEvidenceIntelligenceAnalyzer.analyze(filtered_report, struct_analysis, reasoner)

        # 6. Build ScenarioProfile
        reinforcement_dist = {}
        for sg in intel_profile.signal_groups:
            lvl_str = sg.reinforcement_level.value
            reinforcement_dist[lvl_str] = reinforcement_dist.get(lvl_str, 0) + 1

        profile = ScenarioProfile(
            scenario_id=context.scenario_id,
            scenario_type=context.scenario_type,
            included_drugs=included_drugs,
            excluded_drugs=excluded_drugs,
            surviving_edges_count=filtered_ev_summary.pairs_with_evidence,
            surviving_convergent_edges_count=filtered_ev_summary.convergent_evidence_pairs,
            surviving_themes_count=len([t for t in intel_profile.themes if t.theme_name != "UNKNOWN_OR_UNMAPPED_THEME"]),
            prescription_status=filtered_ev_summary.prescription_status.value,
            topology_classification=struct_analysis.topology.primary_topology.value,
            dominant_theme=intel_profile.summary.dominant_theme,
            evidence_concentration=intel_profile.summary.dominant_evidence_concentration.value,
            reinforcement_level_distribution=reinforcement_dist
        )

        return profile, struct_analysis, intel_profile
