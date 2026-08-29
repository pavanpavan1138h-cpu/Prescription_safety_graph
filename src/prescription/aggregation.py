"""
prescription_aggregation.py

Evidence Aggregation Engine for Phase 6.
Aggregates pair-level inferences into prescription-level distributions and drug participation metrics.
"""

from typing import List, Dict, Tuple
from collections import defaultdict
from src.prescription.schemas import (
    PrescriptionResolutionResult,
    PrescriptionEvidenceSummary,
    DrugParticipationSummary,
    PrescriptionStatus
)
from src.reasoning.schemas import (
    SafetyInferenceResult,
    EvidenceStatus
)
from src.prescription.risk_engine import PrescriptionRiskEngine

class PrescriptionAggregator:
    @staticmethod
    def aggregate_evidence(
        res_summary: PrescriptionResolutionResult,
        pair_inferences: List[Tuple[int, SafetyInferenceResult, str, str]],
        drug_name_map: Dict[str, str]
    ) -> Tuple[PrescriptionEvidenceSummary, List[DrugParticipationSummary]]:
        """
        Computes prescription-level metrics, evidence counts, and drug participation summaries.
        """
        n_unique_drugs = len(res_summary.canonical_drug_ids)
        expected_pairs = (n_unique_drugs * (n_unique_drugs - 1)) // 2 if n_unique_drugs >= 2 else 0
        analyzed_pairs = len(pair_inferences)

        convergent_count = 0
        ddi_only_count = 0
        combination_only_count = 0
        no_direct_count = 0

        # Drug participation counters: drug_id -> stats dict
        drug_stats = defaultdict(lambda: {
            "total_pairs": 0,
            "evidence_pairs": 0,
            "convergent": 0,
            "ddi_only": 0,
            "combination_only": 0,
            "no_evidence": 0
        })

        for _, res, _, _ in pair_inferences:
            st = res.evidence_status
            d1 = res.drug_a_id
            d2 = res.drug_b_id

            drug_stats[d1]["total_pairs"] += 1
            drug_stats[d2]["total_pairs"] += 1

            if st == EvidenceStatus.CONVERGENT_SAFETY_EVIDENCE:
                convergent_count += 1
                drug_stats[d1]["evidence_pairs"] += 1
                drug_stats[d1]["convergent"] += 1
                drug_stats[d2]["evidence_pairs"] += 1
                drug_stats[d2]["convergent"] += 1
            elif st == EvidenceStatus.DDI_EVIDENCE_ONLY:
                ddi_only_count += 1
                drug_stats[d1]["evidence_pairs"] += 1
                drug_stats[d1]["ddi_only"] += 1
                drug_stats[d2]["evidence_pairs"] += 1
                drug_stats[d2]["ddi_only"] += 1
            elif st == EvidenceStatus.COMBINATION_EVENT_EVIDENCE_ONLY:
                combination_only_count += 1
                drug_stats[d1]["evidence_pairs"] += 1
                drug_stats[d1]["combination_only"] += 1
                drug_stats[d2]["evidence_pairs"] += 1
                drug_stats[d2]["combination_only"] += 1
            else: # NO_DIRECT_GRAPH_EVIDENCE
                no_direct_count += 1
                drug_stats[d1]["no_evidence"] += 1
                drug_stats[d2]["no_evidence"] += 1

        pairs_with_ev = convergent_count + ddi_only_count + combination_only_count

        status = PrescriptionRiskEngine.stratify_prescription(
            total_analyzed_pairs=analyzed_pairs,
            convergent_count=convergent_count,
            ddi_only_count=ddi_only_count,
            combination_only_count=combination_only_count,
            no_direct_count=no_direct_count,
            unresolved_count=len(res_summary.unresolved_inputs)
        )

        ev_summary = PrescriptionEvidenceSummary(
            total_input_items=len(res_summary.original_inputs),
            unique_canonical_drugs=n_unique_drugs,
            unresolved_items_count=len(res_summary.unresolved_inputs),
            ambiguous_items_count=len(res_summary.ambiguous_inputs),
            duplicates_collapsed_count=len(res_summary.duplicate_inputs),
            total_expected_pairs=expected_pairs,
            total_analyzed_pairs=analyzed_pairs,
            pairs_with_evidence=pairs_with_ev,
            convergent_evidence_pairs=convergent_count,
            ddi_only_pairs=ddi_only_count,
            combination_event_only_pairs=combination_only_count,
            no_direct_evidence_pairs=no_direct_count,
            prescription_status=status
        )

        # Build drug participation summaries
        participation_list = []
        for cid in res_summary.canonical_drug_ids:
            st = drug_stats[cid]
            dname = drug_name_map.get(cid, cid)
            participation_list.append(DrugParticipationSummary(
                internal_drug_id=cid,
                display_name=dname,
                total_pairs_involved=st["total_pairs"],
                evidence_supported_pairs=st["evidence_pairs"],
                convergent_pairs=st["convergent"],
                ddi_only_pairs=st["ddi_only"],
                combination_event_pairs=st["combination_only"],
                no_evidence_pairs=st["no_evidence"]
            ))

        # Sort participation by evidence pairs (desc)
        participation_list.sort(key=lambda d: (d.evidence_supported_pairs, d.total_pairs_involved), reverse=True)

        return ev_summary, participation_list
