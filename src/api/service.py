"""
src/api/service.py

Service layer adapter managing in-memory engine lifecycle, caching, and serialization.
Wraps PrescriptionSafetyReasoner and SafetyQueryEngine cleanly.
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from collections import defaultdict

from src.api.config import settings
from src.api.schemas import (
    HealthResponse,
    SystemInfoResponse,
    DrugResolveResponse,
    ResolvedDrugItem,
    DrugEntityCardResponse,
    PairSafetyResponse,
    PrescriptionAnalysisResponse,
    AnalysisMetadata,
    InputSummary,
    ResolutionSummary,
    ResolvedDrugCanonicalItem,
    PrescriptionSummary,
    PrioritizedFindingCard,
    PairResultRow,
    DrugParticipationRow,
    UnresolvedItemRow,
    ProvenanceSummary,
    PairDetailResponse,
    DirectDDIItem,
    AdverseEventItem,
    CombinationAdverseEventsDetail,
    ProvenanceTraceDetail
)

# Import Phase 5 & 6 core modules
from src.prescription.reasoning import PrescriptionSafetyReasoner
from src.prescription.schemas import PrescriptionSafetyReport
from src.reasoning.schemas import EvidenceStatus

logger = logging.getLogger(__name__)

class PrescriptionService:
    def __init__(self):
        self.graph_dir = settings.graph_data_dir
        logger.info(f"Initializing PrescriptionService singleton with graph directory: {self.graph_dir}")
        self.reasoner = PrescriptionSafetyReasoner(self.graph_dir)
        self.reasoner.safety_engine.retriever.load()
        
        # Tier 2 Analysis Result Cache: canonical_key -> PrescriptionAnalysisResponse
        self._analysis_cache: Dict[str, PrescriptionAnalysisResponse] = {}
        # Tier 3 UI Retrieval Cache: analysis_id -> PrescriptionSafetyReport
        self._report_objects: Dict[str, PrescriptionSafetyReport] = {}
        # Phase 11 Comparison Cache: comparison_id -> PrescriptionComparativeIntelligenceProfile
        self._comparison_profiles: Dict[str, Any] = {}
        
        self.is_ready = True
        logger.info("PrescriptionService startup initialization completed successfully.")

    def get_system_info(self) -> SystemInfoResponse:
        return SystemInfoResponse(
            api_version=settings.api_version,
            graph_nodes=68223,
            graph_edges=4969811,
            node_breakdown={
                "Drug": 1836,
                "RxNormConcept": 1597,
                "DrugPair": 63473,
                "SideEffect": 1317
            },
            edge_breakdown={
                "HAS_RXNORM_CONCEPT": 1616,
                "INTERACTS_WITH": 191808,
                "MEMBER_OF_PAIR": 126946,
                "ASSOCIATED_WITH": 4649441
            },
            supported_identifier_types=[
                "drug_name",
                "internal_drug_id",
                "drugbank_id",
                "pubchem_cid",
                "rxcui"
            ]
        )

    def resolve_drugs(self, drug_inputs: List[str]) -> DrugResolveResponse:
        res = self.reasoner.resolver.resolve_prescription(drug_inputs)
        
        results_list = []
        for d in res.resolved_drugs:
            results_list.append(ResolvedDrugItem(
                input=d.original_input,
                status=d.resolution_status.value,
                internal_drug_id=d.resolved_internal_drug_id,
                canonical_name=d.display_name,
                identifier_type_matched=d.identifier_type_matched,
                rxcui=d.rxcui
            ))
            
        return DrugResolveResponse(
            input_count=len(drug_inputs),
            unique_resolved_drugs=len(res.canonical_drug_ids),
            duplicates_collapsed=len(res.duplicate_inputs),
            unresolved_count=len(res.unresolved_inputs),
            results=results_list
        )

    def get_drug_card(self, identifier: str) -> Optional[DrugEntityCardResponse]:
        drug = self.reasoner.safety_engine.lookup_drug(identifier)
        if not drug:
            return None
        return DrugEntityCardResponse(
            internal_drug_id=drug.internal_drug_id,
            display_name=drug.display_name,
            entity_status=drug.entity_status,
            source_membership=drug.source_membership,
            rxcui=drug.rxcui,
            rxnorm_name=drug.rxnorm_name,
            rxnorm_match_status=drug.rxnorm_match_status,
            drugbank_ids=drug.drugbank_ids,
            twosides_cids=drug.twosides_cids
        )

    def evaluate_pair(self, drug_a: str, drug_b: str) -> Optional[PairSafetyResponse]:
        res = self.reasoner.safety_engine.evaluate_pair(drug_a, drug_b)
        if not res:
            return None
            
        d_a = self.reasoner.safety_engine.lookup_drug(drug_a)
        d_b = self.reasoner.safety_engine.lookup_drug(drug_b)
        
        return PairSafetyResponse(
            inference_id=res.inference_id,
            drug_a={
                "internal_drug_id": res.drug_a_id,
                "display_name": d_a.display_name if d_a else res.drug_a_id
            },
            drug_b={
                "internal_drug_id": res.drug_b_id,
                "display_name": d_b.display_name if d_b else res.drug_b_id
            },
            evidence_status=res.evidence_status.value,
            confidence={
                "level": res.confidence_level.value,
                "score": res.confidence_score
            },
            evidence_summary={
                "ddi_present": res.ddi_evidence_present,
                "ddi_forward_count": res.ddi_forward_count,
                "ddi_reverse_count": res.ddi_reverse_count,
                "events_present": res.combination_event_present,
                "event_count": res.combination_event_count
            },
            clinical_interpretation=res.clinical_interpretation
        )

    def analyze_prescription(self, medications: List[str], prescription_id: Optional[str] = None) -> PrescriptionAnalysisResponse:
        # Check Tier 2 cache by canonical key
        res_preview = self.reasoner.resolver.resolve_prescription(medications)
        canonical_key = "|".join(sorted(res_preview.canonical_drug_ids))
        
        # Execute Phase 6 analysis
        report = self.reasoner.analyze_prescription(medications, prescription_id)
        self._report_objects[report.prescription_id] = report

        # Transform internal report to public Pydantic schema
        metadata = AnalysisMetadata(
            analysis_id=report.prescription_id,
            api_version=settings.api_version,
            generated_at=report.generated_at,
            graph_version="phase4_frozen_68k_nodes",
            reasoning_engine_version="phase6_multi_drug_v1"
        )

        input_summary = InputSummary(
            submitted_medication_count=len(report.resolution_summary.original_inputs),
            submitted_medications=report.resolution_summary.original_inputs
        )

        # Build canonical grouped items
        canonical_inputs = defaultdict(list)
        for d in report.resolution_summary.resolved_drugs:
            if d.resolved_internal_drug_id:
                canonical_inputs[d.resolved_internal_drug_id].append(d.original_input)

        resolved_canonical_items = []
        for cid in report.resolution_summary.canonical_drug_ids:
            drug_obj = self.reasoner.safety_engine.lookup_drug(cid)
            resolved_canonical_items.append(ResolvedDrugCanonicalItem(
                canonical_drug_id=cid,
                canonical_name=drug_obj.display_name if drug_obj else cid,
                rxcui=drug_obj.rxcui if drug_obj else None,
                input_values=canonical_inputs.get(cid, [cid])
            ))

        resolution_summary = ResolutionSummary(
            resolved_count=len(report.resolution_summary.resolved_drugs) - len(report.resolution_summary.unresolved_inputs),
            unique_canonical_drug_count=len(report.resolution_summary.canonical_drug_ids),
            duplicate_count=len(report.resolution_summary.duplicate_inputs),
            unresolved_count=len(report.resolution_summary.unresolved_inputs),
            resolved_drugs=resolved_canonical_items
        )

        # Highest priority finding
        highest_priority = report.prioritized_findings[0].evidence_priority.value if report.prioritized_findings else "NO_EVIDENCE_PRIORITY"

        prescription_summary = PrescriptionSummary(
            evidence_status=report.evidence_summary.prescription_status.value,
            highest_evidence_priority=highest_priority,
            total_unique_drugs=report.evidence_summary.unique_canonical_drugs,
            total_pairs_analyzed=report.evidence_summary.total_analyzed_pairs,
            positive_evidence_pairs=report.evidence_summary.pairs_with_evidence,
            convergent_evidence_pairs=report.evidence_summary.convergent_evidence_pairs,
            ddi_only_pairs=report.evidence_summary.ddi_only_pairs,
            combination_event_only_pairs=report.evidence_summary.combination_event_only_pairs,
            no_direct_evidence_pairs=report.evidence_summary.no_direct_evidence_pairs
        )

        prioritized_cards = []
        for f in report.prioritized_findings:
            sorted_pair = sorted([f.drug_a_id, f.drug_b_id])
            pair_key = f"PAIR_{sorted_pair[0]}__{sorted_pair[1]}"
            prioritized_cards.append(PrioritizedFindingCard(
                finding_id=f.finding_id,
                pair_id=pair_key,
                priority=f.evidence_priority.value,
                drug_a={"drug_id": f.drug_a_id, "name": f.drug_a_name},
                drug_b={"drug_id": f.drug_b_id, "name": f.drug_b_name},
                evidence_status=f.evidence_status,
                confidence={
                    "level": f.confidence_level,
                    "score": f.confidence_score
                },
                summary_narrative=f.summary_narrative,
                evidence_channels={
                    "drugbank_ddi": f.ddi_present,
                    "twosides_combination_events": f.events_present
                },
                ddi_record_count=f.ddi_count,
                adverse_event_count=f.event_count,
                inference_id=f.inference_id,
                supporting_edge_ids=f.supporting_edge_ids
            ))

        pair_result_rows = []
        for pr in report.pair_results:
            pair_result_rows.append(PairResultRow(
                pair_id=pr["canonical_pair_key"],
                drug_a_name=pr["drug_a_name"],
                drug_b_name=pr["drug_b_name"],
                evidence_status=pr["evidence_status"],
                evidence_priority="CRITICAL_EVIDENCE_PRIORITY" if pr["evidence_status"] == EvidenceStatus.CONVERGENT_SAFETY_EVIDENCE.value else "MODERATE_EVIDENCE_PRIORITY",
                confidence_level=pr["confidence_level"],
                confidence_score=pr["confidence_score"],
                ddi_evidence_present=pr["ddi_present"],
                combination_event_evidence_present=pr["events_present"]
            ))

        drug_participation_rows = []
        for dp in report.drug_participation:
            hp = "CRITICAL_EVIDENCE_PRIORITY" if dp.convergent_pairs > 0 else ("MODERATE_EVIDENCE_PRIORITY" if dp.evidence_supported_pairs > 0 else "NO_EVIDENCE_PRIORITY")
            drug_participation_rows.append(DrugParticipationRow(
                drug_id=dp.internal_drug_id,
                drug_name=dp.display_name,
                total_pairs=dp.total_pairs_involved,
                pairs_with_evidence=dp.evidence_supported_pairs,
                convergent_evidence_pairs=dp.convergent_pairs,
                highest_priority=hp
            ))

        unresolved_rows = []
        for unres in report.resolution_summary.unresolved_inputs:
            unresolved_rows.append(UnresolvedItemRow(
                input_value=unres,
                resolution_status="UNRESOLVED",
                reason="NO_MATCHING_CANONICAL_ENTITY"
            ))

        # Provenance summary aggregation
        all_edges = []
        for f in report.prioritized_findings:
            all_edges.extend(f.supporting_edge_ids)

        provenance_summary = ProvenanceSummary(
            evidence_sources=["DrugBank", "TWOSIDES", "RxNorm"],
            supporting_edge_count=len(all_edges),
            top_supporting_edge_ids=all_edges[:5]
        )

        response_obj = PrescriptionAnalysisResponse(
            metadata=metadata,
            input_summary=input_summary,
            resolution_summary=resolution_summary,
            prescription_summary=prescription_summary,
            prioritized_findings=prioritized_cards,
            pair_results=pair_result_rows,
            drug_participation=drug_participation_rows,
            unresolved_items=unresolved_rows,
            limitations=report.scientific_limitations,
            provenance=provenance_summary,
            clinical_narrative_report=report.clinical_narrative_report
        )

        self._analysis_cache[canonical_key] = response_obj
        return response_obj

    def get_pair_detail(self, analysis_id: str, pair_id: str) -> Optional[PairDetailResponse]:
        # Extract drug IDs from pair_id (e.g. PAIR_DRUG_000006__DRUG_000048 or DRUG_000006__DRUG_000048)
        clean_pair = pair_id.replace("PAIR_", "")
        parts = clean_pair.split("__")
        if len(parts) != 2:
            return None
            
        d1_id, d2_id = parts[0], parts[1]
        bundle = self.reasoner.safety_engine.retriever.retrieve_pair_evidence(d1_id, d2_id)
        inference = self.reasoner.safety_engine.evaluate_pair(d1_id, d2_id)
        if not inference:
            return None

        # Build DDI items
        ddi_items = []
        for ddi in (bundle.ddi_records_forward + bundle.ddi_records_reverse):
            ddi_items.append(DirectDDIItem(
                edge_id=ddi.edge_id,
                direction=f"{ddi.source_drug_id} -> {ddi.target_drug_id}",
                source_dataset="drugbank",
                source_record_id=f"DDI:{ddi.source_drugbank_id_1}:{ddi.source_drugbank_id_2}",
                interaction_description=ddi.interaction_description
            ))

        # Build Side effect items
        ae_items = []
        for se in bundle.side_effect_records:
            ae_items.append(AdverseEventItem(
                edge_id=se.edge_id,
                side_effect_id=se.side_effect_id,
                side_effect_name=se.side_effect_name,
                source_dataset="twosides"
            ))

        d_a = self.reasoner.safety_engine.lookup_drug(d1_id)
        d_b = self.reasoner.safety_engine.lookup_drug(d2_id)

        paths = inference.reasoning_trace.graph_paths if inference.reasoning_trace else []
        reasons = inference.reasoning_trace.confidence_reasons if inference.reasoning_trace else []

        return PairDetailResponse(
            pair_id=pair_id,
            drug_a={
                "internal_drug_id": d1_id,
                "display_name": d_a.display_name if d_a else d1_id,
                "rxcui": d_a.rxcui if d_a else None,
                "rxnorm_name": d_a.rxnorm_name if d_a else None
            },
            drug_b={
                "internal_drug_id": d2_id,
                "display_name": d_b.display_name if d_b else d2_id,
                "rxcui": d_b.rxcui if d_b else None,
                "rxnorm_name": d_b.rxnorm_name if d_b else None
            },
            inference={
                "inference_id": inference.inference_id,
                "evidence_status": inference.evidence_status.value,
                "evidence_priority": "CRITICAL_EVIDENCE_PRIORITY" if inference.evidence_status == EvidenceStatus.CONVERGENT_SAFETY_EVIDENCE else "MODERATE_EVIDENCE_PRIORITY",
                "confidence_level": inference.confidence_level.value,
                "confidence_score": inference.confidence_score,
                "rule_fired": inference.inference_rule
            },
            direct_ddi_evidence=ddi_items,
            combination_adverse_events=CombinationAdverseEventsDetail(
                total_event_count=bundle.total_side_effects_count,
                observed_events=ae_items
            ),
            provenance_trace=ProvenanceTraceDetail(
                graph_paths=paths,
                confidence_reasons=reasons
            )
        )

    def get_structural_analysis(self, analysis_id: str):
        from src.prescription.structural.prescription_structural_analyzer import PrescriptionStructuralAnalyzer
        from src.api.advanced_schemas import (
            PrescriptionStructuralAnalysisSchema,
            NetworkSummarySchema,
            TopologyClassificationSchema,
            ClusterMetricsSchema,
            DrugStructuralProfileSchema,
            CounterfactualResultSchema,
            PrescriptionEvidenceNetworkSchema,
            PrescriptionEvidenceNodeSchema,
            PrescriptionEvidenceEdgeSchema,
            StructuralInterpretationSchema
        )

        report_obj = self._report_objects.get(analysis_id)
        if not report_obj:
            return None

        struct_analysis = PrescriptionStructuralAnalyzer.analyze(report_obj)

        return PrescriptionStructuralAnalysisSchema(
            analysis_id=struct_analysis.analysis_id,
            generated_at=struct_analysis.generated_at,
            network_summary=NetworkSummarySchema(
                total_prescription_drugs=struct_analysis.network_summary.total_prescription_drugs,
                evidence_connected_drugs=struct_analysis.network_summary.evidence_connected_drugs,
                structurally_isolated_drugs=struct_analysis.network_summary.structurally_isolated_drugs,
                total_possible_pairs=struct_analysis.network_summary.total_possible_pairs,
                evidence_supported_pairs=struct_analysis.network_summary.evidence_supported_pairs,
                network_density=struct_analysis.network_summary.network_density,
                connected_cluster_count=struct_analysis.network_summary.connected_cluster_count,
                largest_cluster_size=struct_analysis.network_summary.largest_cluster_size,
                convergent_edge_count=struct_analysis.network_summary.convergent_edge_count,
                ddi_only_edge_count=struct_analysis.network_summary.ddi_only_edge_count,
                combination_event_edge_count=struct_analysis.network_summary.combination_event_edge_count
            ),
            topology=TopologyClassificationSchema(
                primary_topology=struct_analysis.topology.primary_topology.value,
                secondary_characteristics=struct_analysis.topology.secondary_characteristics
            ),
            clusters=[
                ClusterMetricsSchema(
                    cluster_id=c.cluster_id,
                    drug_ids=c.drug_ids,
                    edge_count=c.edge_count,
                    density=c.density,
                    convergent_edge_count=c.convergent_edge_count,
                    ddi_only_edge_count=c.ddi_only_edge_count,
                    combination_event_edge_count=c.combination_event_edge_count,
                    is_isolated=c.is_isolated
                ) for c in struct_analysis.clusters
            ],
            drug_structural_profiles=[
                DrugStructuralProfileSchema(
                    drug_id=dp.drug_id,
                    display_name=dp.display_name,
                    evidence_degree=dp.evidence_degree,
                    weighted_evidence_degree=dp.weighted_evidence_degree,
                    degree_centrality=dp.degree_centrality,
                    betweenness_centrality=dp.betweenness_centrality,
                    evidence_channel_diversity=dp.evidence_channel_diversity,
                    convergent_relationship_count=dp.convergent_relationship_count,
                    ddi_only_relationship_count=dp.ddi_only_relationship_count,
                    combination_only_relationship_count=dp.combination_only_relationship_count,
                    cluster_id=dp.cluster_id,
                    cluster_size=dp.cluster_size,
                    centrality_rank=dp.centrality_rank,
                    structural_contribution_level=dp.structural_contribution_level,
                    structural_contribution_score=dp.structural_contribution_score,
                    explanation=dp.explanation
                ) for dp in struct_analysis.drug_structural_profiles
            ],
            ranked_structural_contributors=[
                DrugStructuralProfileSchema(
                    drug_id=dp.drug_id,
                    display_name=dp.display_name,
                    evidence_degree=dp.evidence_degree,
                    weighted_evidence_degree=dp.weighted_evidence_degree,
                    degree_centrality=dp.degree_centrality,
                    betweenness_centrality=dp.betweenness_centrality,
                    evidence_channel_diversity=dp.evidence_channel_diversity,
                    convergent_relationship_count=dp.convergent_relationship_count,
                    ddi_only_relationship_count=dp.ddi_only_relationship_count,
                    combination_only_relationship_count=dp.combination_only_relationship_count,
                    cluster_id=dp.cluster_id,
                    cluster_size=dp.cluster_size,
                    centrality_rank=dp.centrality_rank,
                    structural_contribution_level=dp.structural_contribution_level,
                    structural_contribution_score=dp.structural_contribution_score,
                    explanation=dp.explanation
                ) for dp in struct_analysis.ranked_structural_contributors
            ],
            counterfactual_results=[
                CounterfactualResultSchema(
                    drug_id=cf.drug_id,
                    display_name=cf.display_name,
                    original_edge_count=cf.original_edge_count,
                    remaining_edge_count=cf.remaining_edge_count,
                    structural_delta=cf.structural_delta,
                    convergent_edges_removed=cf.convergent_edges_removed,
                    clusters_before=cf.clusters_before,
                    clusters_after=cf.clusters_after,
                    largest_cluster_before=cf.largest_cluster_before,
                    largest_cluster_after=cf.largest_cluster_after,
                    contribution_level=cf.contribution_level.value,
                    explanation=cf.explanation
                ) for cf in struct_analysis.counterfactual_results
            ],
            original_network=PrescriptionEvidenceNetworkSchema(
                nodes={
                    k: PrescriptionEvidenceNodeSchema(
                        drug_id=node.drug_id,
                        display_name=node.display_name
                    ) for k, node in struct_analysis.original_network.nodes.items()
                },
                edges={
                    k: PrescriptionEvidenceEdgeSchema(
                        drug_a_id=edge.drug_a_id,
                        drug_b_id=edge.drug_b_id,
                        evidence_status=edge.evidence_status,
                        confidence_score=edge.confidence_score,
                        priority_tier=edge.priority_tier,
                        structural_weight=edge.structural_weight,
                        edge_strength=edge.edge_strength,
                        canonical_pair_key=edge.canonical_pair_key
                    ) for k, edge in struct_analysis.original_network.edges.items()
                },
                canonical_drug_ids=struct_analysis.original_network.canonical_drug_ids
            ),
            structural_interpretation=StructuralInterpretationSchema(
                highest_participation_drug=struct_analysis.structural_interpretation.highest_participation_drug,
                highest_participation_degree=struct_analysis.structural_interpretation.highest_participation_degree,
                network_connectivity_narration=struct_analysis.structural_interpretation.network_connectivity_narration,
                counterfactual_impact_narration=struct_analysis.structural_interpretation.counterfactual_impact_narration,
                clinical_warning=struct_analysis.structural_interpretation.clinical_warning
            ),
            scientific_guardrails=struct_analysis.scientific_guardrails
        )

    def get_structural_drugs(self, analysis_id: str):
        analysis = self.get_structural_analysis(analysis_id)
        return analysis.ranked_structural_contributors if analysis else None

    def get_structural_clusters(self, analysis_id: str):
        analysis = self.get_structural_analysis(analysis_id)
        return analysis.clusters if analysis else None

    def get_structural_counterfactuals(self, analysis_id: str):
        analysis = self.get_structural_analysis(analysis_id)
        return analysis.counterfactual_results if analysis else None

    def get_evidence_intelligence(self, analysis_id: str):
        report_obj = self._report_objects.get(analysis_id)
        if not report_obj:
            return None
        
        from src.prescription.structural.prescription_structural_analyzer import PrescriptionStructuralAnalyzer
        struct_analysis = PrescriptionStructuralAnalyzer.analyze(report_obj)

        from src.prescription.intelligence.intelligence_aggregator import PrescriptionEvidenceIntelligenceAnalyzer
        intel_profile = PrescriptionEvidenceIntelligenceAnalyzer.analyze(report_obj, struct_analysis, self.reasoner)

        from src.api.advanced_schemas import (
            PrescriptionEvidenceIntelligenceProfileSchema,
            EvidenceThemeSchema,
            CrossPairSignalGroupSchema,
            EvidenceConcentrationProfileSchema,
            StructuralEvidenceAlignmentSchema,
            DrugAlignmentProfileSchema,
            EvidenceIntelligenceSummarySchema
        )

        return PrescriptionEvidenceIntelligenceProfileSchema(
            analysis_id=intel_profile.analysis_id,
            generated_at=intel_profile.generated_at,
            themes=[
                EvidenceThemeSchema(
                    theme_id=t.theme_id,
                    theme_name=t.theme_name,
                    description=t.description,
                    mapped_events=t.mapped_events,
                    supporting_pairs=t.supporting_pairs,
                    participating_drugs=t.participating_drugs,
                    supporting_evidence_count=t.supporting_evidence_count,
                    convergent_pair_count=t.convergent_pair_count,
                    source_channels=t.source_channels
                ) for t in intel_profile.themes
            ],
            signal_groups=[
                CrossPairSignalGroupSchema(
                    group_id=sg.group_id,
                    theme_id=sg.theme_id,
                    supporting_pairs=sg.supporting_pairs,
                    participating_drugs=sg.participating_drugs,
                    supporting_events=sg.supporting_events,
                    channel_distribution=sg.channel_distribution,
                    convergent_pair_count=sg.convergent_pair_count,
                    reinforcement_score=sg.reinforcement_score,
                    reinforcement_level=sg.reinforcement_level.value
                ) for sg in intel_profile.signal_groups
            ],
            concentration_profile=EvidenceConcentrationProfileSchema(
                concentration_type=intel_profile.concentration_profile.concentration_type.value,
                edge_coverage_ratio=intel_profile.concentration_profile.edge_coverage_ratio,
                dominant_drug_id=intel_profile.concentration_profile.dominant_drug_id,
                dominant_drug_share=intel_profile.concentration_profile.dominant_drug_share,
                dominant_cluster_id=intel_profile.concentration_profile.dominant_cluster_id,
                dominant_cluster_edge_share=intel_profile.concentration_profile.dominant_cluster_edge_share
            ) if intel_profile.concentration_profile else None,
            structural_evidence_alignment=StructuralEvidenceAlignmentSchema(
                alignment_level=intel_profile.structural_evidence_alignment.alignment_level.value,
                explanation=intel_profile.structural_evidence_alignment.explanation,
                drug_alignment_profiles=[
                    DrugAlignmentProfileSchema(
                        drug_id=dap.drug_id,
                        display_name=dap.display_name,
                        structural_rank=dap.structural_rank,
                        evidence_participation_rank=dap.evidence_participation_rank,
                        theme_participation_rank=dap.theme_participation_rank,
                        convergent_evidence_rank=dap.convergent_evidence_rank,
                        alignment_score=dap.alignment_score,
                        alignment_level=dap.alignment_level.value
                    ) for dap in intel_profile.structural_evidence_alignment.drug_alignment_profiles
                ]
            ) if intel_profile.structural_evidence_alignment else None,
            summary=EvidenceIntelligenceSummarySchema(
                major_theme_count=intel_profile.summary.major_theme_count,
                reinforced_signal_group_count=intel_profile.summary.reinforced_signal_group_count,
                dominant_theme=intel_profile.summary.dominant_theme,
                dominant_evidence_concentration=intel_profile.summary.dominant_evidence_concentration.value,
                strongest_reinforcement_level=intel_profile.summary.strongest_reinforcement_level.value,
                highest_alignment_level=intel_profile.summary.highest_alignment_level.value,
                overall_intelligence_pattern=intel_profile.summary.overall_intelligence_pattern
            ) if intel_profile.summary else None,
            narrative=intel_profile.narrative,
            guardrails=intel_profile.guardrails
        )

    def get_intelligence_themes(self, analysis_id: str):
        intel = self.get_evidence_intelligence(analysis_id)
        return intel.themes if intel else None

    def get_intelligence_signals(self, analysis_id: str):
        intel = self.get_evidence_intelligence(analysis_id)
        return intel.signal_groups if intel else None

    def get_intelligence_concentration(self, analysis_id: str):
        intel = self.get_evidence_intelligence(analysis_id)
        return intel.concentration_profile if intel else None

    def get_intelligence_alignment(self, analysis_id: str):
        intel = self.get_evidence_intelligence(analysis_id)
        return intel.structural_evidence_alignment if intel else None

    def get_contextual_stability(self, analysis_id: str):
        report_obj = self._report_objects.get(analysis_id)
        if not report_obj:
            return None
        
        from src.prescription.structural.prescription_structural_analyzer import PrescriptionStructuralAnalyzer
        struct_analysis = PrescriptionStructuralAnalyzer.analyze(report_obj)

        from src.prescription.contextual.contextual_aggregator import ContextualStabilityAggregator
        stability_profile = ContextualStabilityAggregator.analyze(report_obj, struct_analysis, self.reasoner)

        from src.api.advanced_schemas import (
            ContextualStabilityProfileSchema,
            ScenarioProfileSchema,
            EvidenceStabilityScoreSchema,
            SignalPersistenceSchema,
            ContextSensitivitySchema,
            DrugDependencyImpactSchema
        )

        return ContextualStabilityProfileSchema(
            analysis_id=stability_profile.analysis_id,
            generated_at=stability_profile.generated_at,
            scenarios=[
                ScenarioProfileSchema(
                    scenario_id=s.scenario_id,
                    scenario_type=s.scenario_type.value,
                    included_drugs=s.included_drugs,
                    excluded_drugs=s.excluded_drugs,
                    surviving_edges_count=s.surviving_edges_count,
                    surviving_convergent_edges_count=s.surviving_convergent_edges_count,
                    surviving_themes_count=s.surviving_themes_count,
                    prescription_status=s.prescription_status,
                    topology_classification=s.topology_classification,
                    dominant_theme=s.dominant_theme,
                    evidence_concentration=s.evidence_concentration,
                    reinforcement_level_distribution=s.reinforcement_level_distribution
                ) for s in stability_profile.scenarios
            ],
            evidence_stability=EvidenceStabilityScoreSchema(
                overall_stability_score=stability_profile.evidence_stability.overall_stability_score,
                pair_preservation_ratio=stability_profile.evidence_stability.pair_preservation_ratio,
                convergent_preservation_ratio=stability_profile.evidence_stability.convergent_preservation_ratio,
                theme_preservation_ratio=stability_profile.evidence_stability.theme_preservation_ratio,
                structural_edge_preservation_ratio=stability_profile.evidence_stability.structural_edge_preservation_ratio
            ),
            signal_persistences=[
                SignalPersistenceSchema(
                    theme_name=sp.theme_name,
                    persistence_score=sp.persistence_score,
                    persistence_level=sp.persistence_level
                ) for sp in stability_profile.signal_persistences
            ],
            context_sensitivity=ContextSensitivitySchema(
                overall_sensitivity_score=stability_profile.context_sensitivity.overall_sensitivity_score,
                sensitivity_level=stability_profile.context_sensitivity.sensitivity_level,
                status_change_rate=stability_profile.context_sensitivity.status_change_rate,
                topology_change_rate=stability_profile.context_sensitivity.topology_change_rate,
                theme_change_rate=stability_profile.context_sensitivity.theme_change_rate
            ),
            drug_dependencies=[
                DrugDependencyImpactSchema(
                    drug_id=dep.drug_id,
                    display_name=dep.display_name,
                    dependency_score=dep.dependency_score,
                    dependency_level=dep.dependency_level,
                    edge_loss_ratio=dep.edge_loss_ratio,
                    theme_loss_ratio=dep.theme_loss_ratio,
                    structural_connectivity_loss_ratio=dep.structural_connectivity_loss_ratio
                ) for dep in stability_profile.drug_dependencies
            ],
            interpretation_stability=stability_profile.interpretation_stability.value,
            summary_narrative=stability_profile.summary_narrative,
            guardrails=stability_profile.guardrails
        )

    def get_contextual_scenarios(self, analysis_id: str):
        prof = self.get_contextual_stability(analysis_id)
        return prof.scenarios if prof else None

    def get_contextual_metrics(self, analysis_id: str):
        prof = self.get_contextual_stability(analysis_id)
        return prof.evidence_stability if prof else None

    def get_contextual_dependency(self, analysis_id: str):
        prof = self.get_contextual_stability(analysis_id)
        return prof.drug_dependencies if prof else None

    def analyze_prescription_advanced(self, medications: List[str], prescription_id: Optional[str] = None):
        from src.prescription.advanced_intelligence_service import AdvancedIntelligenceService
        from src.prescription.structural.prescription_structural_analyzer import PrescriptionStructuralAnalyzer
        from src.prescription.intelligence.intelligence_aggregator import PrescriptionEvidenceIntelligenceAnalyzer
        from src.prescription.contextual.contextual_aggregator import ContextualStabilityAggregator
        from src.api.advanced_schemas import (
            AdvancedPrescriptionAnalysisResponse,
            ComplexityProfileSchema,
            DrugParticipationProfileSchema,
            AdverseEventConvergenceSchema,
            EvidencePatternSchema,
            ReviewPriorityFindingSchema,
            UncertaintyProfileSchema,
            ClinicalContextRequirementSchema,
            AdvancedExplanationSchema,
            # Phase 8 structural schemas
            PrescriptionStructuralAnalysisSchema,
            NetworkSummarySchema,
            TopologyClassificationSchema,
            ClusterMetricsSchema,
            DrugStructuralProfileSchema,
            CounterfactualResultSchema,
            PrescriptionEvidenceNetworkSchema,
            PrescriptionEvidenceNodeSchema,
            PrescriptionEvidenceEdgeSchema,
            StructuralInterpretationSchema,
            # Phase 9 intelligence schemas
            PrescriptionEvidenceIntelligenceProfileSchema,
            EvidenceThemeSchema,
            CrossPairSignalGroupSchema,
            EvidenceConcentrationProfileSchema,
            StructuralEvidenceAlignmentSchema,
            DrugAlignmentProfileSchema,
            EvidenceIntelligenceSummarySchema,
            # Phase 10 contextual schemas
            ContextualStabilityProfileSchema,
            ScenarioProfileSchema,
            EvidenceStabilityScoreSchema,
            SignalPersistenceSchema,
            ContextSensitivitySchema,
            DrugDependencyImpactSchema
        )

        base_res = self.analyze_prescription(medications, prescription_id)
        adv_service = AdvancedIntelligenceService(self.reasoner)
        report_obj, adv_report = adv_service.analyze_advanced(medications, base_res.metadata.analysis_id)

        # Execute Phase 8 structural safety analysis
        struct_analysis = PrescriptionStructuralAnalyzer.analyze(report_obj)

        # Execute Phase 9 evidence intelligence analysis
        intel_profile = PrescriptionEvidenceIntelligenceAnalyzer.analyze(report_obj, struct_analysis, self.reasoner)

        # Execute Phase 10 contextual stability analysis
        stability_profile = ContextualStabilityAggregator.analyze(report_obj, struct_analysis, self.reasoner)

        return AdvancedPrescriptionAnalysisResponse(
            prescription_report=base_res,
            complexity_profile=ComplexityProfileSchema(
                complexity_category=adv_report.complexity_profile.complexity_category.value,
                unique_drugs_count=adv_report.complexity_profile.unique_drugs_count,
                generated_pairs_count=adv_report.complexity_profile.generated_pairs_count,
                positive_pairs_count=adv_report.complexity_profile.positive_pairs_count,
                convergent_pairs_count=adv_report.complexity_profile.convergent_pairs_count,
                participating_drugs_count=adv_report.complexity_profile.participating_drugs_count,
                max_single_drug_participation_ratio=adv_report.complexity_profile.max_single_drug_participation_ratio,
                unresolved_inputs_count=adv_report.complexity_profile.unresolved_inputs_count,
                complexity_score=adv_report.complexity_profile.complexity_score,
                explanation=adv_report.complexity_profile.explanation
            ),
            drug_participation_profiles=[
                DrugParticipationProfileSchema(
                    internal_drug_id=dp.internal_drug_id,
                    display_name=dp.display_name,
                    participation_category=dp.participation_category.value,
                    total_evaluated_pairs=dp.total_evaluated_pairs,
                    positive_evidence_pairs=dp.positive_evidence_pairs,
                    convergent_evidence_pairs=dp.convergent_evidence_pairs,
                    ddi_participation_count=dp.ddi_participation_count,
                    event_participation_count=dp.event_participation_count,
                    prescription_findings_ratio=dp.prescription_findings_ratio,
                    relative_evidence_concentration=dp.relative_evidence_concentration,
                    explanation=dp.explanation
                ) for dp in adv_report.drug_participation_profiles
            ],
            event_convergence_items=[
                AdverseEventConvergenceSchema(
                    side_effect_name=ec.side_effect_name,
                    side_effect_id=ec.side_effect_id,
                    participating_pairs_count=ec.participating_pairs_count,
                    participating_pair_keys=ec.participating_pair_keys,
                    participating_drug_ids=ec.participating_drug_ids,
                    participating_drug_names=ec.participating_drug_names,
                    convergence_category=ec.convergence_category.value,
                    explanation=ec.explanation
                ) for ec in adv_report.event_convergence_items
            ],
            evidence_patterns=[
                EvidencePatternSchema(
                    pattern_id=ep.pattern_id,
                    pattern_type=ep.pattern_type.value,
                    title=ep.title,
                    supporting_pair_ids=ep.supporting_pair_ids,
                    supporting_drug_ids=ep.supporting_drug_ids,
                    supporting_drug_names=ep.supporting_drug_names,
                    evidence_counts=ep.evidence_counts,
                    rule_fired=ep.rule_fired,
                    explanation=ep.explanation,
                    provenance_edge_ids=ep.provenance_edge_ids
                ) for ep in adv_report.evidence_patterns
            ],
            review_priorities=[
                ReviewPriorityFindingSchema(
                    finding_id=rp.finding_id,
                    pair_id=rp.pair_id,
                    drug_a_name=rp.drug_a_name,
                    drug_b_name=rp.drug_b_name,
                    review_priority=rp.review_priority.value,
                    review_score=rp.review_score,
                    deterministic_reasons=rp.deterministic_reasons,
                    evidence_status=rp.evidence_status,
                    confidence_score=rp.confidence_score,
                    inference_id=rp.inference_id,
                    supporting_edge_ids=rp.supporting_edge_ids
                ) for rp in adv_report.review_priorities
            ],
            uncertainty_profile=UncertaintyProfileSchema(
                uncertainty_categories=[c.value for c in adv_report.uncertainty_profile.uncertainty_categories],
                has_identity_uncertainty=adv_report.uncertainty_profile.has_identity_uncertainty,
                unresolved_input_names=adv_report.uncertainty_profile.unresolved_input_names,
                unmapped_rxnorm_drugs=adv_report.uncertainty_profile.unmapped_rxnorm_drugs,
                single_channel_only_pairs=adv_report.uncertainty_profile.single_channel_only_pairs,
                unsupported_pairs_count=adv_report.uncertainty_profile.unsupported_pairs_count,
                uncertainty_level=adv_report.uncertainty_profile.uncertainty_level,
                explanation_narrative=adv_report.uncertainty_profile.explanation_narrative
            ),
            clinical_context_requirements=[
                ClinicalContextRequirementSchema(
                    context_category=cc.context_category,
                    description=cc.description,
                    why_it_matters=cc.why_it_matters,
                    is_available_in_graph=cc.is_available_in_graph,
                    is_evaluated_by_system=cc.is_evaluated_by_system
                ) for cc in adv_report.clinical_context_requirements
            ],
            advanced_explanation=AdvancedExplanationSchema(
                executive_summary=adv_report.advanced_explanation.executive_summary,
                key_findings_summary=adv_report.advanced_explanation.key_findings_summary,
                prescription_patterns_summary=adv_report.advanced_explanation.prescription_patterns_summary,
                uncertainty_summary=adv_report.advanced_explanation.uncertainty_summary,
                scientific_guardrails=adv_report.advanced_explanation.scientific_guardrails
            ),
            scientific_limitations=adv_report.scientific_limitations,
            # Phase 8 Structural Analysis Integration
            structural_analysis=PrescriptionStructuralAnalysisSchema(
                analysis_id=struct_analysis.analysis_id,
                generated_at=struct_analysis.generated_at,
                network_summary=NetworkSummarySchema(
                    total_prescription_drugs=struct_analysis.network_summary.total_prescription_drugs,
                    evidence_connected_drugs=struct_analysis.network_summary.evidence_connected_drugs,
                    structurally_isolated_drugs=struct_analysis.network_summary.structurally_isolated_drugs,
                    total_possible_pairs=struct_analysis.network_summary.total_possible_pairs,
                    evidence_supported_pairs=struct_analysis.network_summary.evidence_supported_pairs,
                    network_density=struct_analysis.network_summary.network_density,
                    connected_cluster_count=struct_analysis.network_summary.connected_cluster_count,
                    largest_cluster_size=struct_analysis.network_summary.largest_cluster_size,
                    convergent_edge_count=struct_analysis.network_summary.convergent_edge_count,
                    ddi_only_edge_count=struct_analysis.network_summary.ddi_only_edge_count,
                    combination_event_edge_count=struct_analysis.network_summary.combination_event_edge_count
                ),
                topology=TopologyClassificationSchema(
                    primary_topology=struct_analysis.topology.primary_topology.value,
                    secondary_characteristics=struct_analysis.topology.secondary_characteristics
                ),
                clusters=[
                    ClusterMetricsSchema(
                        cluster_id=c.cluster_id,
                        drug_ids=c.drug_ids,
                        edge_count=c.edge_count,
                        density=c.density,
                        convergent_edge_count=c.convergent_edge_count,
                        ddi_only_edge_count=c.ddi_only_edge_count,
                        combination_event_edge_count=c.combination_event_edge_count,
                        is_isolated=c.is_isolated
                    ) for c in struct_analysis.clusters
                ],
                drug_structural_profiles=[
                    DrugStructuralProfileSchema(
                        drug_id=dp.drug_id,
                        display_name=dp.display_name,
                        evidence_degree=dp.evidence_degree,
                        weighted_evidence_degree=dp.weighted_evidence_degree,
                        degree_centrality=dp.degree_centrality,
                        betweenness_centrality=dp.betweenness_centrality,
                        evidence_channel_diversity=dp.evidence_channel_diversity,
                        convergent_relationship_count=dp.convergent_relationship_count,
                        ddi_only_relationship_count=dp.ddi_only_relationship_count,
                        combination_only_relationship_count=dp.combination_only_relationship_count,
                        cluster_id=dp.cluster_id,
                        cluster_size=dp.cluster_size,
                        centrality_rank=dp.centrality_rank,
                        structural_contribution_level=dp.structural_contribution_level,
                        structural_contribution_score=dp.structural_contribution_score,
                        explanation=dp.explanation
                    ) for dp in struct_analysis.drug_structural_profiles
                ],
                ranked_structural_contributors=[
                    DrugStructuralProfileSchema(
                        drug_id=dp.drug_id,
                        display_name=dp.display_name,
                        evidence_degree=dp.evidence_degree,
                        weighted_evidence_degree=dp.weighted_evidence_degree,
                        degree_centrality=dp.degree_centrality,
                        betweenness_centrality=dp.betweenness_centrality,
                        evidence_channel_diversity=dp.evidence_channel_diversity,
                        convergent_relationship_count=dp.convergent_relationship_count,
                        ddi_only_relationship_count=dp.ddi_only_relationship_count,
                        combination_only_relationship_count=dp.combination_only_relationship_count,
                        cluster_id=dp.cluster_id,
                        cluster_size=dp.cluster_size,
                        centrality_rank=dp.centrality_rank,
                        structural_contribution_level=dp.structural_contribution_level,
                        structural_contribution_score=dp.structural_contribution_score,
                        explanation=dp.explanation
                    ) for dp in struct_analysis.ranked_structural_contributors
                ],
                counterfactual_results=[
                    CounterfactualResultSchema(
                        drug_id=cf.drug_id,
                        display_name=cf.display_name,
                        original_edge_count=cf.original_edge_count,
                        remaining_edge_count=cf.remaining_edge_count,
                        structural_delta=cf.structural_delta,
                        convergent_edges_removed=cf.convergent_edges_removed,
                        clusters_before=cf.clusters_before,
                        clusters_after=cf.clusters_after,
                        largest_cluster_before=cf.largest_cluster_before,
                        largest_cluster_after=cf.largest_cluster_after,
                        contribution_level=cf.contribution_level.value,
                        explanation=cf.explanation
                    ) for cf in struct_analysis.counterfactual_results
                ],
                original_network=PrescriptionEvidenceNetworkSchema(
                    nodes={
                        k: PrescriptionEvidenceNodeSchema(
                            drug_id=node.drug_id,
                            display_name=node.display_name
                        ) for k, node in struct_analysis.original_network.nodes.items()
                    },
                    edges={
                        k: PrescriptionEvidenceEdgeSchema(
                            drug_a_id=edge.drug_a_id,
                            drug_b_id=edge.drug_b_id,
                            evidence_status=edge.evidence_status,
                            confidence_score=edge.confidence_score,
                            priority_tier=edge.priority_tier,
                            structural_weight=edge.structural_weight,
                            edge_strength=edge.edge_strength,
                            canonical_pair_key=edge.canonical_pair_key
                        ) for k, edge in struct_analysis.original_network.edges.items()
                    },
                    canonical_drug_ids=struct_analysis.original_network.canonical_drug_ids
                ),
                structural_interpretation=StructuralInterpretationSchema(
                    highest_participation_drug=struct_analysis.structural_interpretation.highest_participation_drug,
                    highest_participation_degree=struct_analysis.structural_interpretation.highest_participation_degree,
                    network_connectivity_narration=struct_analysis.structural_interpretation.network_connectivity_narration,
                    counterfactual_impact_narration=struct_analysis.structural_interpretation.counterfactual_impact_narration,
                    clinical_warning=struct_analysis.structural_interpretation.clinical_warning
                ),
                scientific_guardrails=struct_analysis.scientific_guardrails
            ),
            evidence_intelligence=PrescriptionEvidenceIntelligenceProfileSchema(
                analysis_id=intel_profile.analysis_id,
                generated_at=intel_profile.generated_at,
                themes=[
                    EvidenceThemeSchema(
                        theme_id=t.theme_id,
                        theme_name=t.theme_name,
                        description=t.description,
                        mapped_events=t.mapped_events,
                        supporting_pairs=t.supporting_pairs,
                        participating_drugs=t.participating_drugs,
                        supporting_evidence_count=t.supporting_evidence_count,
                        convergent_pair_count=t.convergent_pair_count,
                        source_channels=t.source_channels
                    ) for t in intel_profile.themes
                ],
                signal_groups=[
                    CrossPairSignalGroupSchema(
                        group_id=sg.group_id,
                        theme_id=sg.theme_id,
                        supporting_pairs=sg.supporting_pairs,
                        participating_drugs=sg.participating_drugs,
                        supporting_events=sg.supporting_events,
                        channel_distribution=sg.channel_distribution,
                        convergent_pair_count=sg.convergent_pair_count,
                        reinforcement_score=sg.reinforcement_score,
                        reinforcement_level=sg.reinforcement_level.value
                    ) for sg in intel_profile.signal_groups
                ],
                concentration_profile=EvidenceConcentrationProfileSchema(
                    concentration_type=intel_profile.concentration_profile.concentration_type.value,
                    edge_coverage_ratio=intel_profile.concentration_profile.edge_coverage_ratio,
                    dominant_drug_id=intel_profile.concentration_profile.dominant_drug_id,
                    dominant_drug_share=intel_profile.concentration_profile.dominant_drug_share,
                    dominant_cluster_id=intel_profile.concentration_profile.dominant_cluster_id,
                    dominant_cluster_edge_share=intel_profile.concentration_profile.dominant_cluster_edge_share
                ) if intel_profile.concentration_profile else None,
                structural_evidence_alignment=StructuralEvidenceAlignmentSchema(
                    alignment_level=intel_profile.structural_evidence_alignment.alignment_level.value,
                    explanation=intel_profile.structural_evidence_alignment.explanation,
                    drug_alignment_profiles=[
                        DrugAlignmentProfileSchema(
                            drug_id=dap.drug_id,
                            display_name=dap.display_name,
                            structural_rank=dap.structural_rank,
                            evidence_participation_rank=dap.evidence_participation_rank,
                            theme_participation_rank=dap.theme_participation_rank,
                            convergent_evidence_rank=dap.convergent_evidence_rank,
                            alignment_score=dap.alignment_score,
                            alignment_level=dap.alignment_level.value
                        ) for dap in intel_profile.structural_evidence_alignment.drug_alignment_profiles
                    ]
                ) if intel_profile.structural_evidence_alignment else None,
                summary=EvidenceIntelligenceSummarySchema(
                    major_theme_count=intel_profile.summary.major_theme_count,
                    reinforced_signal_group_count=intel_profile.summary.reinforced_signal_group_count,
                    dominant_theme=intel_profile.summary.dominant_theme,
                    dominant_evidence_concentration=intel_profile.summary.dominant_evidence_concentration.value,
                    strongest_reinforcement_level=intel_profile.summary.strongest_reinforcement_level.value,
                    highest_alignment_level=intel_profile.summary.highest_alignment_level.value,
                    overall_intelligence_pattern=intel_profile.summary.overall_intelligence_pattern
                ) if intel_profile.summary else None,
                narrative=intel_profile.narrative,
                guardrails=intel_profile.guardrails
            ),
            contextual_stability=ContextualStabilityProfileSchema(
                analysis_id=stability_profile.analysis_id,
                generated_at=stability_profile.generated_at,
                scenarios=[
                    ScenarioProfileSchema(
                        scenario_id=s.scenario_id,
                        scenario_type=s.scenario_type.value,
                        included_drugs=s.included_drugs,
                        excluded_drugs=s.excluded_drugs,
                        surviving_edges_count=s.surviving_edges_count,
                        surviving_convergent_edges_count=s.surviving_convergent_edges_count,
                        surviving_themes_count=s.surviving_themes_count,
                        prescription_status=s.prescription_status,
                        topology_classification=s.topology_classification,
                        dominant_theme=s.dominant_theme,
                        evidence_concentration=s.evidence_concentration,
                        reinforcement_level_distribution=s.reinforcement_level_distribution
                    ) for s in stability_profile.scenarios
                ],
                evidence_stability=EvidenceStabilityScoreSchema(
                    overall_stability_score=stability_profile.evidence_stability.overall_stability_score,
                    pair_preservation_ratio=stability_profile.evidence_stability.pair_preservation_ratio,
                    convergent_preservation_ratio=stability_profile.evidence_stability.convergent_preservation_ratio,
                    theme_preservation_ratio=stability_profile.evidence_stability.theme_preservation_ratio,
                    structural_edge_preservation_ratio=stability_profile.evidence_stability.structural_edge_preservation_ratio
                ),
                signal_persistences=[
                    SignalPersistenceSchema(
                        theme_name=sp.theme_name,
                        persistence_score=sp.persistence_score,
                        persistence_level=sp.persistence_level
                    ) for sp in stability_profile.signal_persistences
                ],
                context_sensitivity=ContextSensitivitySchema(
                    overall_sensitivity_score=stability_profile.context_sensitivity.overall_sensitivity_score,
                    sensitivity_level=stability_profile.context_sensitivity.sensitivity_level,
                    status_change_rate=stability_profile.context_sensitivity.status_change_rate,
                    topology_change_rate=stability_profile.context_sensitivity.topology_change_rate,
                    theme_change_rate=stability_profile.context_sensitivity.theme_change_rate
                ),
                drug_dependencies=[
                    DrugDependencyImpactSchema(
                        drug_id=dep.drug_id,
                        display_name=dep.display_name,
                        dependency_score=dep.dependency_score,
                        dependency_level=dep.dependency_level,
                        edge_loss_ratio=dep.edge_loss_ratio,
                        theme_loss_ratio=dep.theme_loss_ratio,
                        structural_connectivity_loss_ratio=dep.structural_connectivity_loss_ratio
                    ) for dep in stability_profile.drug_dependencies
                ],
                interpretation_stability=stability_profile.interpretation_stability.value,
                summary_narrative=stability_profile.summary_narrative,
                guardrails=stability_profile.guardrails
            ),
            explainability=self.get_explainability_profile(base_res.metadata.analysis_id),
            trustworthiness=self.get_trustworthiness_profile(base_res.metadata.analysis_id)
        )

    def get_trustworthiness_profile(self, analysis_id: str):
        report_obj = self._report_objects.get(analysis_id)
        if not report_obj:
            return None

        # Re-resolve all layers deterministically
        from src.prescription.structural.prescription_structural_analyzer import PrescriptionStructuralAnalyzer
        struct_analysis = PrescriptionStructuralAnalyzer.analyze(report_obj)

        from src.prescription.intelligence.intelligence_aggregator import PrescriptionEvidenceIntelligenceAnalyzer
        intel_profile = PrescriptionEvidenceIntelligenceAnalyzer.analyze(report_obj, struct_analysis, self.reasoner)

        from src.prescription.contextual.contextual_aggregator import ContextualStabilityAggregator
        stability_profile = ContextualStabilityAggregator.analyze(report_obj, struct_analysis, self.reasoner)

        explainability_profile = self.get_explainability_profile(analysis_id)

        # Baseline medications extracted from resolved drugs list
        meds = []
        if report_obj.resolution_summary:
            for d in report_obj.resolution_summary.resolved_drugs:
                meds.append(getattr(d, "original_input", ""))

        # Define wrapper call for the perturbation runner
        def run_analysis_wrapper(inputs: List[str]):
            # Runs advanced analysis in memory using ADV service
            from src.prescription.advanced_intelligence_service import AdvancedIntelligenceService
            adv_service = AdvancedIntelligenceService(self.reasoner)
            # Use mock ID for perturbation run
            r_obj, _ = adv_service.analyze_advanced(inputs, f"PERT_{analysis_id}")
            return r_obj

        from src.prescription.trustworthiness.trustworthiness_aggregator import TrustworthinessAggregator
        trust_profile = TrustworthinessAggregator.analyze_trustworthiness(
            baseline_meds=meds,
            baseline_report=report_obj,
            structural_analysis=struct_analysis,
            evidence_intelligence=intel_profile,
            contextual_stability=stability_profile,
            explainability_profile=explainability_profile,
            analyze_func=run_analysis_wrapper
        )

        from src.api.advanced_schemas import (
            PrescriptionTrustworthinessProfileSchema,
            ReproducibilityProfileSchema,
            InputPerturbationResultSchema,
            StructuralRobustnessProfileSchema,
            SignalRobustnessProfileSchema,
            CrossLayerConsistencyProfileSchema,
            ProvenanceCompletenessProfileSchema,
            ExplanationConsistencyProfileSchema,
            TrustworthinessMetricSchema
        )

        return PrescriptionTrustworthinessProfileSchema(
            prescription_id=trust_profile.prescription_id,
            analysis_id=trust_profile.analysis_id,
            generated_at=trust_profile.generated_at,
            reproducibility_profile=ReproducibilityProfileSchema(
                baseline_signature=trust_profile.reproducibility_profile.baseline_signature,
                repeat_run_signatures=trust_profile.reproducibility_profile.repeat_run_signatures,
                deterministic_match_ratio=trust_profile.reproducibility_profile.deterministic_match_ratio,
                classification=trust_profile.reproducibility_profile.classification.value,
                mismatched_components=trust_profile.reproducibility_profile.mismatched_components
            ),
            input_perturbation_results=[
                InputPerturbationResultSchema(
                    perturbation_id=p.perturbation_id,
                    perturbation_type=p.perturbation_type.value,
                    baseline_signature=p.baseline_signature,
                    perturbed_signature=p.perturbed_signature,
                    invariant_components=p.invariant_components,
                    changed_components=p.changed_components,
                    classification=p.classification.value
                ) for p in trust_profile.input_perturbation_results
            ],
            structural_robustness=StructuralRobustnessProfileSchema(
                baseline_topology=trust_profile.structural_robustness.baseline_topology,
                scenario_topology_distribution=trust_profile.structural_robustness.scenario_topology_distribution,
                topology_persistence_ratio=trust_profile.structural_robustness.topology_persistence_ratio,
                cluster_persistence_ratio=trust_profile.structural_robustness.cluster_persistence_ratio,
                central_participant_persistence=trust_profile.structural_robustness.central_participant_persistence,
                robustness_level=trust_profile.structural_robustness.robustness_level.value
            ),
            signal_robustness_profiles=[
                SignalRobustnessProfileSchema(
                    theme_id=sr.theme_id,
                    baseline_present=sr.baseline_present,
                    scenario_presence_ratio=sr.scenario_presence_ratio,
                    reinforcement_stability=sr.reinforcement_stability,
                    classification=sr.classification.value
                ) for sr in trust_profile.signal_robustness_profiles
            ],
            cross_layer_consistency=CrossLayerConsistencyProfileSchema(
                structural_dominant_participants=trust_profile.cross_layer_consistency.structural_dominant_participants,
                evidence_dominant_participants=trust_profile.cross_layer_consistency.evidence_dominant_participants,
                dependency_dominant_participants=trust_profile.cross_layer_consistency.dependency_dominant_participants,
                primary_contributors=trust_profile.cross_layer_consistency.primary_contributors,
                shared_participants=trust_profile.cross_layer_consistency.shared_participants,
                consistency_level=trust_profile.cross_layer_consistency.consistency_level.value,
                explanation=trust_profile.cross_layer_consistency.explanation
            ),
            provenance_completeness=ProvenanceCompletenessProfileSchema(
                traceability_coverage=trust_profile.provenance_completeness.traceability_coverage,
                average_provenance_depth=trust_profile.provenance_completeness.average_provenance_depth,
                orphaned_component_count=trust_profile.provenance_completeness.orphaned_component_count,
                cross_layer_traceability=trust_profile.provenance_completeness.cross_layer_traceability,
                completeness_level=trust_profile.provenance_completeness.completeness_level
            ),
            explanation_consistency=ExplanationConsistencyProfileSchema(
                claims_checked=trust_profile.explanation_consistency.claims_checked,
                claims_supported=trust_profile.explanation_consistency.claims_supported,
                unsupported_claims=trust_profile.explanation_consistency.unsupported_claims,
                consistency_ratio=trust_profile.explanation_consistency.consistency_ratio,
                classification=trust_profile.explanation_consistency.classification
            ),
            trustworthiness_metrics=[
                TrustworthinessMetricSchema(
                    metric_id=tm.metric_id,
                    metric_name=tm.metric_name,
                    value=tm.value,
                    normalized_value=tm.normalized_value,
                    classification=tm.classification,
                    description=tm.description
                ) for tm in trust_profile.trustworthiness_metrics
            ],
            overall_trustworthiness_level=trust_profile.overall_trustworthiness_level.value,
            executive_summary=trust_profile.executive_summary,
            guardrails=trust_profile.guardrails
        )

    def get_trustworthiness_reproducibility(self, analysis_id: str):
        prof = self.get_trustworthiness_profile(analysis_id)
        return prof.reproducibility_profile if prof else None

    def get_trustworthiness_perturbations(self, analysis_id: str):
        prof = self.get_trustworthiness_profile(analysis_id)
        return prof.input_perturbation_results if prof else None

    def get_trustworthiness_structure(self, analysis_id: str):
        prof = self.get_trustworthiness_profile(analysis_id)
        return prof.structural_robustness if prof else None

    def get_trustworthiness_signals(self, analysis_id: str):
        prof = self.get_trustworthiness_profile(analysis_id)
        return prof.signal_robustness_profiles if prof else None

    def get_trustworthiness_cross_layer(self, analysis_id: str):
        prof = self.get_trustworthiness_profile(analysis_id)
        return prof.cross_layer_consistency if prof else None

    def get_trustworthiness_provenance(self, analysis_id: str):
        prof = self.get_trustworthiness_profile(analysis_id)
        return prof.provenance_completeness if prof else None

    def get_trustworthiness_explanation_consistency(self, analysis_id: str):
        prof = self.get_trustworthiness_profile(analysis_id)
        return prof.explanation_consistency if prof else None

    def get_explainability_profile(self, analysis_id: str):
        report_obj = self._report_objects.get(analysis_id)
        if not report_obj:
            return None

        from src.prescription.structural.prescription_structural_analyzer import PrescriptionStructuralAnalyzer
        struct_analysis = PrescriptionStructuralAnalyzer.analyze(report_obj)

        from src.prescription.intelligence.intelligence_aggregator import PrescriptionEvidenceIntelligenceAnalyzer
        intel_profile = PrescriptionEvidenceIntelligenceAnalyzer.analyze(report_obj, struct_analysis, self.reasoner)

        from src.prescription.contextual.contextual_aggregator import ContextualStabilityAggregator
        stability_profile = ContextualStabilityAggregator.analyze(report_obj, struct_analysis, self.reasoner)

        from src.prescription.explainability.explainability_aggregator import ExplainabilityAggregator
        explainability_aggregator = ExplainabilityAggregator()
        exp_profile = explainability_aggregator.generate_explainability_profile(
            analysis_result=report_obj,
            structural_analysis=struct_analysis,
            evidence_intelligence=intel_profile,
            contextual_stability=stability_profile
        )

        from src.api.advanced_schemas import (
            PrescriptionExplainabilityProfileSchema,
            ExplanationGraphSchema,
            ExplanationNodeSchema,
            ExplanationEdgeSchema,
            ContributionProfileSchema,
            DecisionDependencyMapSchema,
            DependencyNodeSchema,
            TraceabilityProfileSchema,
            SourceProvenanceRecordSchema,
            StructuredExplanationClaimSchema
        )

        return PrescriptionExplainabilityProfileSchema(
            prescription_id=exp_profile.prescription_id,
            analysis_id=exp_profile.analysis_id,
            generated_at=exp_profile.generated_at,
            explanation_graph=ExplanationGraphSchema(
                nodes=[
                    ExplanationNodeSchema(
                        node_id=n.node_id,
                        node_type=n.node_type.value,
                        label=n.label,
                        description=n.description,
                        phase_origin=n.phase_origin,
                        source_reference=n.source_reference,
                        metadata=n.metadata
                    ) for n in exp_profile.explanation_graph.nodes
                ],
                edges=[
                    ExplanationEdgeSchema(
                        edge_id=e.edge_id,
                        source_node_id=e.source_node_id,
                        target_node_id=e.target_node_id,
                        relationship_type=e.relationship_type.value,
                        contribution_weight=e.contribution_weight,
                        description=e.description
                    ) for e in exp_profile.explanation_graph.edges
                ],
                root_node_ids=exp_profile.explanation_graph.root_node_ids,
                leaf_node_ids=exp_profile.explanation_graph.leaf_node_ids
            ),
            contribution_profiles=[
                ContributionProfileSchema(
                    entity_id=cp.entity_id,
                    entity_label=cp.entity_label,
                    entity_type=cp.entity_type,
                    direct_decision_contribution=cp.direct_decision_contribution,
                    evidence_coverage=cp.evidence_coverage,
                    cross_layer_participation=cp.cross_layer_participation,
                    dependency_impact=cp.dependency_impact,
                    overall_contribution_score=cp.overall_contribution_score,
                    contribution_level=cp.contribution_level.value,
                    participating_phases=cp.participating_phases,
                    explanation=cp.explanation
                ) for cp in exp_profile.contribution_profiles
            ],
            dependency_map=DecisionDependencyMapSchema(
                target_interpretation_id=exp_profile.dependency_map.target_interpretation_id,
                dependencies=[
                    DependencyNodeSchema(
                        entity_id=d.entity_id,
                        entity_label=d.entity_label,
                        entity_type=d.entity_type,
                        depends_on_ids=d.depends_on_ids,
                        dependency_weight=d.dependency_weight,
                        critical_dependency=d.critical_dependency
                    ) for d in exp_profile.dependency_map.dependencies
                ],
                critical_path_entities=exp_profile.dependency_map.critical_path_entities,
                acyclic_verified=exp_profile.dependency_map.acyclic_verified
            ),
            traceability_profile=TraceabilityProfileSchema(
                total_components_evaluated=exp_profile.traceability_profile.total_components_evaluated,
                traceable_components_count=exp_profile.traceability_profile.traceable_components_count,
                traceability_coverage_score=exp_profile.traceability_profile.traceability_coverage_score,
                average_provenance_depth=exp_profile.traceability_profile.average_provenance_depth,
                max_provenance_depth=exp_profile.traceability_profile.max_provenance_depth,
                orphaned_components_count=exp_profile.traceability_profile.orphaned_components_count,
                orphaned_component_ids=exp_profile.traceability_profile.orphaned_component_ids,
                cross_layer_traceability=exp_profile.traceability_profile.cross_layer_traceability.value
            ),
            provenance_records=[
                SourceProvenanceRecordSchema(
                    source_id=pr.source_id,
                    dataset_name=pr.dataset_name,
                    record_type=pr.record_type,
                    external_identifier=pr.external_identifier,
                    description=pr.description,
                    is_available=pr.is_available
                ) for pr in exp_profile.provenance_records
            ],
            structured_claims=[
                StructuredExplanationClaimSchema(
                    claim_id=sc.claim_id,
                    claim_type=sc.claim_type,
                    claim_text=sc.claim_text,
                    referenced_entity_ids=sc.referenced_entity_ids,
                    is_supported=sc.is_supported,
                    supporting_evidence_ids=sc.supporting_evidence_ids
                ) for sc in exp_profile.structured_claims
            ],
            narrative=exp_profile.narrative,
            guardrails=exp_profile.guardrails
        )

    def get_explainability_graph(self, analysis_id: str):
        prof = self.get_explainability_profile(analysis_id)
        return prof.explanation_graph if prof else None

    def get_explainability_provenance(self, analysis_id: str):
        prof = self.get_explainability_profile(analysis_id)
        return prof.provenance_records if prof else None

    def get_explainability_contributors(self, analysis_id: str):
        prof = self.get_explainability_profile(analysis_id)
        return prof.contribution_profiles if prof else None

    def get_explainability_dependencies(self, analysis_id: str):
        prof = self.get_explainability_profile(analysis_id)
        return prof.dependency_map if prof else None

    def get_explainability_traceability(self, analysis_id: str):
        prof = self.get_explainability_profile(analysis_id)
        return prof.traceability_profile if prof else None

    def compare_prescriptions(self, analysis_id_a: str, analysis_id_b: str):
        from src.prescription.comparison.comparison_aggregator import PrescriptionComparativeIntelligenceEngine
        profile = PrescriptionComparativeIntelligenceEngine.compare(analysis_id_a, analysis_id_b, self)
        self._comparison_profiles[profile.comparison_id] = profile
        return self.get_comparison_profile(profile.comparison_id)

    def get_comparison_profile(self, comparison_id: str):
        profile = self._comparison_profiles.get(comparison_id)
        if not profile:
            return None
        
        from src.api.advanced_schemas import (
            PrescriptionComparativeIntelligenceProfileSchema,
            MedicationSetComparisonSchema,
            EvidenceDeltaSchema,
            PairComparisonSchema,
            StructuralDeltaSchema,
            DrugRankComparisonSchema,
            SignalDeltaSchema,
            ThemeComparisonSchema,
            StabilityDeltaSchema,
            ComparisonMetricSchema,
            MajorChangeSchema,
            ComparisonSummarySchema
        )

        return PrescriptionComparativeIntelligenceProfileSchema(
            comparison_id=profile.comparison_id,
            analysis_id_a=profile.analysis_id_a,
            analysis_id_b=profile.analysis_id_b,
            medication_set_comparison=MedicationSetComparisonSchema(
                shared_drugs=profile.medication_set_comparison.shared_drugs,
                a_only_drugs=profile.medication_set_comparison.a_only_drugs,
                b_only_drugs=profile.medication_set_comparison.b_only_drugs
            ),
            evidence_delta=EvidenceDeltaSchema(
                pair_comparisons=[
                    PairComparisonSchema(
                        canonical_pair_key=p.canonical_pair_key,
                        drug_a_id=p.drug_a_id,
                        drug_b_id=p.drug_b_id,
                        drug_a_name=p.drug_a_name,
                        drug_b_name=p.drug_b_name,
                        evidence_status_a=p.evidence_status_a,
                        evidence_status_b=p.evidence_status_b,
                        change_type=p.change_type.value
                    ) for p in profile.evidence_delta.pair_comparisons
                ],
                added_pairs_count=profile.evidence_delta.added_pairs_count,
                removed_pairs_count=profile.evidence_delta.removed_pairs_count,
                reclassified_pairs_count=profile.evidence_delta.reclassified_pairs_count,
                preserved_pairs_count=profile.evidence_delta.preserved_pairs_count
            ),
            structural_delta=StructuralDeltaSchema(
                node_count_a=profile.structural_delta.node_count_a,
                node_count_b=profile.structural_delta.node_count_b,
                node_count_delta=profile.structural_delta.node_count_delta,
                edge_count_a=profile.structural_delta.edge_count_a,
                edge_count_b=profile.structural_delta.edge_count_b,
                edge_count_delta=profile.structural_delta.edge_count_delta,
                density_a=profile.structural_delta.density_a,
                density_b=profile.structural_delta.density_b,
                density_delta=profile.structural_delta.density_delta,
                cluster_count_a=profile.structural_delta.cluster_count_a,
                cluster_count_b=profile.structural_delta.cluster_count_b,
                cluster_count_delta=profile.structural_delta.cluster_count_delta,
                topology_a=profile.structural_delta.topology_a,
                topology_b=profile.structural_delta.topology_b,
                topology_changed=profile.structural_delta.topology_changed,
                dominant_drug_a=profile.structural_delta.dominant_drug_a,
                dominant_drug_b=profile.structural_delta.dominant_drug_b,
                dominant_drug_changed=profile.structural_delta.dominant_drug_changed,
                rank_comparisons=[
                    DrugRankComparisonSchema(
                        drug_id=rc.drug_id,
                        display_name=rc.display_name,
                        rank_a=rc.rank_a,
                        rank_b=rc.rank_b,
                        rank_delta=rc.rank_delta,
                        normalized_position_a=rc.normalized_position_a,
                        normalized_position_b=rc.normalized_position_b,
                        normalized_position_delta=rc.normalized_position_delta
                    ) for rc in profile.structural_delta.rank_comparisons
                ],
                structural_delta_magnitude=profile.structural_delta.structural_delta_magnitude
            ),
            signal_delta=SignalDeltaSchema(
                theme_comparisons=[
                    ThemeComparisonSchema(
                        theme_name=tc.theme_name,
                        reinforcement_score_a=tc.reinforcement_score_a,
                        reinforcement_score_b=tc.reinforcement_score_b,
                        reinforcement_level_a=tc.reinforcement_level_a,
                        reinforcement_level_b=tc.reinforcement_level_b,
                        supporting_pairs_a=tc.supporting_pairs_a,
                        supporting_pairs_b=tc.supporting_pairs_b,
                        participating_drugs_a=tc.participating_drugs_a,
                        participating_drugs_b=tc.participating_drugs_b,
                        change_type=tc.change_type.value
                    ) for tc in profile.signal_delta.theme_comparisons
                ],
                concentration_type_a=profile.signal_delta.concentration_type_a,
                concentration_type_b=profile.signal_delta.concentration_type_b,
                concentration_changed=profile.signal_delta.concentration_changed,
                alignment_level_a=profile.signal_delta.alignment_level_a,
                alignment_level_b=profile.signal_delta.alignment_level_b,
                alignment_changed=profile.signal_delta.alignment_changed
            ),
            stability_delta=StabilityDeltaSchema(
                stability_score_a=profile.stability_delta.stability_score_a,
                stability_score_b=profile.stability_delta.stability_score_b,
                stability_score_delta=profile.stability_delta.stability_score_delta,
                sensitivity_score_a=profile.stability_delta.sensitivity_score_a,
                sensitivity_score_b=profile.stability_delta.sensitivity_score_b,
                sensitivity_score_delta=profile.stability_delta.sensitivity_score_delta,
                interpretation_stability_a=profile.stability_delta.interpretation_stability_a,
                interpretation_stability_b=profile.stability_delta.interpretation_stability_b,
                stability_change_type=profile.stability_delta.stability_change_type.value
            ),
            comparison_metrics=[
                ComparisonMetricSchema(
                    metric_name=cm.metric_name,
                    value_a=cm.value_a,
                    value_b=cm.value_b,
                    raw_difference=cm.raw_difference,
                    normalized_difference=cm.normalized_difference
                ) for cm in profile.comparison_metrics
            ],
            major_changes=[
                MajorChangeSchema(
                    category=mc.category,
                    change_type=mc.change_type,
                    affected_entities=mc.affected_entities,
                    magnitude=mc.magnitude,
                    description=mc.description
                ) for mc in profile.major_changes
            ],
            preserved_characteristics=profile.preserved_characteristics,
            summary=ComparisonSummarySchema(
                total_evidence_changes=profile.summary.total_evidence_changes,
                total_structural_changes=profile.summary.total_structural_changes,
                total_signal_changes=profile.summary.total_signal_changes,
                stability_shift=profile.summary.stability_shift,
                global_delta_interpretation=profile.summary.global_delta_interpretation
            ),
            narrative=profile.narrative,
            guardrails=profile.guardrails
        )

    def get_comparison_evidence(self, comparison_id: str):
        prof = self.get_comparison_profile(comparison_id)
        return prof.evidence_delta if prof else None

    def get_comparison_structure(self, comparison_id: str):
        prof = self.get_comparison_profile(comparison_id)
        return prof.structural_delta if prof else None

    def get_comparison_signals(self, comparison_id: str):
        prof = self.get_comparison_profile(comparison_id)
        return prof.signal_delta if prof else None

    def get_comparison_stability(self, comparison_id: str):
        prof = self.get_comparison_profile(comparison_id)
        return prof.stability_delta if prof else None

    # --- Phase 13 Longitudinal Evolution Service Methods ---
    def create_longitudinal_profile(self, analysis_ids: List[str]):
        if not hasattr(self, "_longitudinal_profiles"):
            self._longitudinal_profiles = {}

        # Resolve all matching cached snapshot report objects
        snapshots = []
        for aid in analysis_ids:
            snap = self._report_objects.get(aid)
            if snap:
                # We need to enrich it with explainability and trustworthiness so aggregator gets them
                if not hasattr(snap, "explainability") or snap.explainability is None:
                    snap.explainability = self.get_explainability_profile(aid)
                if not hasattr(snap, "trustworthiness") or snap.trustworthiness is None:
                    snap.trustworthiness = self.get_trustworthiness_profile(aid)
                snapshots.append(snap)

        if not snapshots:
            return None

        from src.prescription.longitudinal.longitudinal_aggregator import LongitudinalAggregator
        profile = LongitudinalAggregator.aggregate_longitudinal_profile(snapshots)

        longitudinal_id = "LONG_" + "_".join(sorted(analysis_ids))
        self._longitudinal_profiles[longitudinal_id] = profile
        return longitudinal_id

    def get_longitudinal_profile(self, longitudinal_id: str):
        if not hasattr(self, "_longitudinal_profiles"):
            return None
        prof = self._longitudinal_profiles.get(longitudinal_id)
        if not prof:
            return None

        from src.api.advanced_schemas import (
            PrescriptionLongitudinalProfileSchema,
            PrescriptionSnapshotReferenceSchema,
            PersistenceProfileSchema,
            EmergenceEventSchema,
            DisappearanceEventSchema,
            LongitudinalChangePointSchema,
            StructuralEvolutionProfileSchema,
            SignalEvolutionProfileSchema,
            StabilityEvolutionProfileSchema,
            TrustworthinessEvolutionProfileSchema,
            CrossLayerEvolutionProfileSchema
        )

        return PrescriptionLongitudinalProfileSchema(
            timeline=[
                PrescriptionSnapshotReferenceSchema(
                    analysis_id=t.analysis_id,
                    prescription_id=t.prescription_id,
                    snapshot_timestamp=t.snapshot_timestamp,
                    sequence_index=t.sequence_index,
                    position_type=t.position_type.value,
                    medications=t.medications
                ) for t in prof.timeline
            ],
            persistence_profiles=[
                PersistenceProfileSchema(
                    entity_id=p.entity_id,
                    entity_type=p.entity_type,
                    presence_ratio=p.presence_ratio,
                    longest_consecutive_run=p.longest_consecutive_run,
                    first_seen_index=p.first_seen_index,
                    last_seen_index=p.last_seen_index,
                    persistence_level=p.persistence_level.value
                ) for p in prof.persistence_profiles
            ],
            emergence_events=[
                EmergenceEventSchema(
                    entity_id=e.entity_id,
                    entity_type=e.entity_type,
                    emergence_index=e.emergence_index,
                    previously_absent_count=e.previously_absent_count,
                    post_emergence_persistence=e.post_emergence_persistence,
                    classification=e.classification.value
                ) for e in prof.emergence_events
            ],
            disappearance_events=[
                DisappearanceEventSchema(
                    entity_id=d.entity_id,
                    entity_type=d.entity_type,
                    disappearance_index=d.disappearance_index,
                    previously_present_count=d.previously_present_count,
                    post_disappearance_absence_ratio=d.post_disappearance_absence_ratio,
                    classification=d.classification.value
                ) for d in prof.disappearance_events
            ],
            change_points=[
                LongitudinalChangePointSchema(
                    from_snapshot_index=cp.from_snapshot_index,
                    to_snapshot_index=cp.to_snapshot_index,
                    structural_change=cp.structural_change,
                    signal_change=cp.signal_change,
                    stability_change=cp.stability_change,
                    trustworthiness_change=cp.trustworthiness_change,
                    medication_set_change=cp.medication_set_change,
                    aggregate_change_score=cp.aggregate_change_score,
                    change_level=cp.change_level.value,
                    contributing_dimensions=cp.contributing_dimensions
                ) for cp in prof.change_points
            ],
            structural_evolution=StructuralEvolutionProfileSchema(
                topology_sequence=prof.structural_evolution.topology_sequence,
                density_sequence=prof.structural_evolution.density_sequence,
                central_participant_sequence=prof.structural_evolution.central_participant_sequence,
                cluster_count_sequence=prof.structural_evolution.cluster_count_sequence,
                topology_transition_count=prof.structural_evolution.topology_transition_count,
                structural_change_points=prof.structural_evolution.structural_change_points,
                classification=prof.structural_evolution.classification.value
            ),
            signal_evolution=[
                SignalEvolutionProfileSchema(
                    theme_id=s.theme_id,
                    presence_sequence=s.presence_sequence,
                    reinforcement_sequence=s.reinforcement_sequence,
                    rank_sequence=s.rank_sequence,
                    persistence_ratio=s.persistence_ratio,
                    emergence_events=[
                        EmergenceEventSchema(
                            entity_id=e.entity_id,
                            entity_type=e.entity_type,
                            emergence_index=e.emergence_index,
                            previously_absent_count=e.previously_absent_count,
                            post_emergence_persistence=e.post_emergence_persistence,
                            classification=e.classification.value
                        ) for e in s.emergence_events
                    ],
                    disappearance_events=[
                        DisappearanceEventSchema(
                            entity_id=d.entity_id,
                            entity_type=d.entity_type,
                            disappearance_index=d.disappearance_index,
                            previously_present_count=d.previously_present_count,
                            post_disappearance_absence_ratio=d.post_disappearance_absence_ratio,
                            classification=d.classification.value
                        ) for d in s.disappearance_events
                    ],
                    classification=s.classification.value
                ) for s in prof.signal_evolution
            ],
            stability_evolution=StabilityEvolutionProfileSchema(
                stability_sequence=prof.stability_evolution.stability_sequence,
                sensitivity_sequence=prof.stability_evolution.sensitivity_sequence,
                transition_count=prof.stability_evolution.transition_count,
                classification=prof.stability_evolution.classification.value
            ),
            trustworthiness_evolution=TrustworthinessEvolutionProfileSchema(
                score_sequence=prof.trustworthiness_evolution.score_sequence,
                level_sequence=prof.trustworthiness_evolution.level_sequence,
                score_delta_sequence=prof.trustworthiness_evolution.score_delta_sequence,
                mean_score=prof.trustworthiness_evolution.mean_score,
                score_volatility=prof.trustworthiness_evolution.score_volatility,
                classification=prof.trustworthiness_evolution.classification.value
            ),
            cross_layer_evolution=CrossLayerEvolutionProfileSchema(
                structural_persistence=prof.cross_layer_evolution.structural_persistence,
                signal_persistence=prof.cross_layer_evolution.signal_persistence,
                stability_persistence=prof.cross_layer_evolution.stability_persistence,
                provenance_persistence=prof.cross_layer_evolution.provenance_persistence,
                trustworthiness_persistence=prof.cross_layer_evolution.trustworthiness_persistence,
                cross_layer_transition_alignment=prof.cross_layer_evolution.cross_layer_transition_alignment,
                classification=prof.cross_layer_evolution.classification,
                explanation=prof.cross_layer_evolution.explanation
            ),
            overall_evolution_level=prof.overall_evolution_level.value,
            longitudinal_summary=prof.longitudinal_summary,
            guardrails=prof.guardrails
        )

    def get_longitudinal_timeline(self, longitudinal_id: str):
        prof = self.get_longitudinal_profile(longitudinal_id)
        return prof.timeline if prof else None

    def get_longitudinal_persistence(self, longitudinal_id: str):
        prof = self.get_longitudinal_profile(longitudinal_id)
        return prof.persistence_profiles if prof else None

    def get_longitudinal_emergence(self, longitudinal_id: str):
        prof = self.get_longitudinal_profile(longitudinal_id)
        return prof.emergence_events if prof else None

    def get_longitudinal_disappearance(self, longitudinal_id: str):
        prof = self.get_longitudinal_profile(longitudinal_id)
        return prof.disappearance_events if prof else None

    def get_longitudinal_change_points(self, longitudinal_id: str):
        prof = self.get_longitudinal_profile(longitudinal_id)
        return prof.change_points if prof else None

    def get_structural_evolution(self, longitudinal_id: str):
        prof = self.get_longitudinal_profile(longitudinal_id)
        return prof.structural_evolution if prof else None

    def get_signal_evolution(self, longitudinal_id: str):
        prof = self.get_longitudinal_profile(longitudinal_id)
        return prof.signal_evolution if prof else None

    def get_stability_evolution(self, longitudinal_id: str):
        prof = self.get_longitudinal_profile(longitudinal_id)
        return prof.stability_evolution if prof else None

    def get_trustworthiness_evolution(self, longitudinal_id: str):
        prof = self.get_longitudinal_profile(longitudinal_id)
        return prof.trustworthiness_evolution if prof else None

    def get_cross_layer_evolution(self, longitudinal_id: str):
        prof = self.get_longitudinal_profile(longitudinal_id)
        return prof.cross_layer_evolution if prof else None

# Global singleton service instance
service_instance: Optional[PrescriptionService] = None

def get_prescription_service() -> PrescriptionService:
    global service_instance
    if service_instance is None:
        service_instance = PrescriptionService()
    return service_instance
