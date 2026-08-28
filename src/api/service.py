"""
src/api/service.py

Service layer adapter managing in-memory engine lifecycle, caching, and serialization.
Wraps PrescriptionSafetyReasoner and SafetyQueryEngine cleanly.
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from collections import defaultdict

from api.config import settings
from api.schemas import (
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
from prescription_reasoning import PrescriptionSafetyReasoner
from prescription_schema import PrescriptionSafetyReport
from reasoning_schema import EvidenceStatus

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

    def analyze_prescription_advanced(self, medications: List[str], prescription_id: Optional[str] = None):
        from advanced_intelligence_service import AdvancedIntelligenceService
        from api.advanced_schemas import (
            AdvancedPrescriptionAnalysisResponse,
            ComplexityProfileSchema,
            DrugParticipationProfileSchema,
            AdverseEventConvergenceSchema,
            EvidencePatternSchema,
            ReviewPriorityFindingSchema,
            UncertaintyProfileSchema,
            ClinicalContextRequirementSchema,
            AdvancedExplanationSchema
        )

        base_res = self.analyze_prescription(medications, prescription_id)
        adv_service = AdvancedIntelligenceService(self.reasoner)
        report_obj, adv_report = adv_service.analyze_advanced(medications, base_res.metadata.analysis_id)

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
            scientific_limitations=adv_report.scientific_limitations
        )

# Global singleton service instance
service_instance: Optional[PrescriptionService] = None

def get_prescription_service() -> PrescriptionService:
    global service_instance
    if service_instance is None:
        service_instance = PrescriptionService()
    return service_instance
