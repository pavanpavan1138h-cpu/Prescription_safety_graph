"""
signal_prioritization.py

Deterministic Signal Prioritization Engine for Phase 6.
Ranks pair-level graph findings into evidence priority tiers based on
multi-channel convergence, confidence scores, DDI presence, and event counts.
Explicit Notice: Evidence Priority != Clinical Severity or Risk Probability.
"""

from typing import List, Tuple
from prescription_schema import (
    EvidencePriority,
    PrioritizedFinding
)
from reasoning_schema import (
    SafetyInferenceResult,
    EvidenceStatus,
    ConfidenceLevel
)

class SignalPrioritizer:
    @staticmethod
    def prioritize_findings(pair_inferences: List[Tuple[int, SafetyInferenceResult, str, str]]) -> List[PrioritizedFinding]:
        """
        Takes a list of (pair_index, SafetyInferenceResult, name_a, name_b) and returns
        a deterministically prioritized list of findings.
        """
        findings: List[PrioritizedFinding] = []
        finding_counter = 1

        for pair_idx, res, name_a, name_b in pair_inferences:
            p_level = SignalPrioritizer._assign_priority(res)
            
            summary_narrative = (
                f"{name_a} ({res.drug_a_id}) + {name_b} ({res.drug_b_id}): "
                f"Classified as {res.evidence_status.value} with {res.confidence_level.value} (Score: {res.confidence_score}). "
                f"DDI evidence: {res.ddi_evidence_present} (fwd: {res.ddi_forward_count}, rev: {res.ddi_reverse_count}), "
                f"TWOSIDES combination events: {res.combination_event_present} ({res.combination_event_count} events)."
            )

            supp_edges = []
            source_recs = []
            if res.reasoning_trace:
                supp_edges = res.reasoning_trace.supporting_edge_ids
                source_recs = res.reasoning_trace.source_record_ids

            finding = PrioritizedFinding(
                finding_id=f"FIND_{finding_counter:04d}",
                pair_index=pair_idx,
                drug_a_id=res.drug_a_id,
                drug_b_id=res.drug_b_id,
                drug_a_name=name_a,
                drug_b_name=name_b,
                evidence_status=res.evidence_status.value,
                evidence_priority=p_level,
                confidence_level=res.confidence_level.value,
                confidence_score=res.confidence_score,
                ddi_present=res.ddi_evidence_present,
                ddi_count=(res.ddi_forward_count + res.ddi_reverse_count),
                events_present=res.combination_event_present,
                event_count=res.combination_event_count,
                inference_id=res.inference_id,
                rule_fired=res.inference_rule,
                summary_narrative=summary_narrative,
                supporting_edge_ids=supp_edges,
                source_record_ids=source_recs
            )
            findings.append(finding)
            finding_counter += 1

        # Deterministic sorting order: Priority Tier -> Confidence Score (desc) -> Event count (desc) -> Pair index
        tier_weights = {
            EvidencePriority.CRITICAL_EVIDENCE_PRIORITY: 5,
            EvidencePriority.HIGH_EVIDENCE_PRIORITY: 4,
            EvidencePriority.MODERATE_EVIDENCE_PRIORITY: 3,
            EvidencePriority.LIMITED_EVIDENCE_PRIORITY: 2,
            EvidencePriority.NO_EVIDENCE_PRIORITY: 1
        }

        findings.sort(
            key=lambda f: (
                tier_weights[f.evidence_priority],
                f.confidence_score,
                f.event_count,
                -f.pair_index
            ),
            reverse=True
        )

        return findings

    @staticmethod
    def _assign_priority(res: SafetyInferenceResult) -> EvidencePriority:
        st = res.evidence_status
        score = res.confidence_score

        # Tier 1: Critical Evidence Priority (Convergent evidence + high confidence)
        if st == EvidenceStatus.CONVERGENT_SAFETY_EVIDENCE and score >= 0.80:
            return EvidencePriority.CRITICAL_EVIDENCE_PRIORITY

        # Tier 2: High Evidence Priority (Convergent evidence moderate confidence OR high confidence DDI)
        if st == EvidenceStatus.CONVERGENT_SAFETY_EVIDENCE:
            return EvidencePriority.HIGH_EVIDENCE_PRIORITY
        if st == EvidenceStatus.DDI_EVIDENCE_ONLY and score >= 0.70:
            return EvidencePriority.HIGH_EVIDENCE_PRIORITY

        # Tier 3: Moderate Evidence Priority (DDI-only or combination events with moderate/high score)
        if st == EvidenceStatus.DDI_EVIDENCE_ONLY:
            return EvidencePriority.MODERATE_EVIDENCE_PRIORITY
        if st == EvidenceStatus.COMBINATION_EVENT_EVIDENCE_ONLY and score >= 0.50:
            return EvidencePriority.MODERATE_EVIDENCE_PRIORITY

        # Tier 4: Limited Evidence Priority (Low-count combination events or ambiguous cases)
        if st == EvidenceStatus.COMBINATION_EVENT_EVIDENCE_ONLY:
            return EvidencePriority.LIMITED_EVIDENCE_PRIORITY

        # Tier 5: No Evidence Priority
        return EvidencePriority.NO_EVIDENCE_PRIORITY
