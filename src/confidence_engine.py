"""
confidence_engine.py

Transparent rule-based Evidence Confidence Engine for Phase 5.
Evaluates identity resolution reliability, cross-source convergence, and ambiguity penalties.
"""

from typing import Tuple, List
from reasoning_schema import (
    PairEvidenceBundle,
    EvidenceStatus,
    ConfidenceLevel
)

class ConfidenceEngine:
    @staticmethod
    def calculate_confidence(
        bundle: PairEvidenceBundle,
        evidence_status: EvidenceStatus
    ) -> Tuple[float, ConfidenceLevel, List[str]]:
        """
        Calculates a transparent confidence score in [0.0, 1.0] and assigns a ConfidenceLevel.
        Returns (score, level, list_of_reasons).
        """
        score = 0.0
        reasons = []

        drug_a = bundle.drug_a
        drug_b = bundle.drug_b

        # 1. Identity Resolution Baseline (up to 0.40)
        is_a_confirmed = (drug_a.entity_status == "CONFIRMED_INTEGRATED_ENTITY")
        is_b_confirmed = (drug_b.entity_status == "CONFIRMED_INTEGRATED_ENTITY")
        is_a_ambiguous = (drug_a.entity_status == "AMBIGUOUS_MAPPING_COMPONENT")
        is_b_ambiguous = (drug_b.entity_status == "AMBIGUOUS_MAPPING_COMPONENT")

        if is_a_confirmed and is_b_confirmed:
            score += 0.25
            reasons.append("Both drug identities are confirmed integrated entities (+0.25).")
        elif is_a_ambiguous or is_b_ambiguous:
            score += 0.10
            reasons.append("One or both drug entities involve ambiguous crosswalk mapping (+0.10).")

        # RxNorm Concept resolution
        has_a_rxn = bool(drug_a.rxcui)
        has_b_rxn = bool(drug_b.rxcui)
        if has_a_rxn and has_b_rxn:
            score += 0.15
            reasons.append("Both drugs resolve to standardized RxNorm concepts (+0.15).")
        elif has_a_rxn or has_b_rxn:
            score += 0.08
            reasons.append("One drug resolves to an RxNorm concept (+0.08).")

        # 2. Evidence Channel Support (up to 0.60)
        if evidence_status == EvidenceStatus.CONVERGENT_SAFETY_EVIDENCE:
            score += 0.60
            reasons.append("Convergent evidence across DrugBank DDI and TWOSIDES combination events (+0.60).")
        elif evidence_status == EvidenceStatus.DDI_EVIDENCE_ONLY:
            score += 0.40
            reasons.append("Documented DrugBank interaction assertions present (+0.40).")
        elif evidence_status == EvidenceStatus.COMBINATION_EVENT_EVIDENCE_ONLY:
            # Scale slightly based on number of observed events
            event_count = bundle.total_side_effects_count
            if event_count >= 50:
                score += 0.40
                reasons.append(f"Extensive TWOSIDES combination observations ({event_count} events) (+0.40).")
            elif event_count >= 10:
                score += 0.30
                reasons.append(f"Moderate TWOSIDES combination observations ({event_count} events) (+0.30).")
            else:
                score += 0.20
                reasons.append(f"Sparse TWOSIDES combination observations ({event_count} events) (+0.20).")
        else: # NO_DIRECT_GRAPH_EVIDENCE
            score += 0.0
            reasons.append("No direct interaction or combination safety signals detected in current graph.")

        # Bound score
        score = min(1.0, max(0.0, round(score, 2)))

        # Assign Categorical Level
        if is_a_ambiguous or is_b_ambiguous:
            level = ConfidenceLevel.AMBIGUOUS_EVIDENCE
        elif score >= 0.80:
            level = ConfidenceLevel.HIGH_EVIDENCE_CONFIDENCE
        elif score >= 0.50:
            level = ConfidenceLevel.MODERATE_EVIDENCE_CONFIDENCE
        else:
            level = ConfidenceLevel.LIMITED_EVIDENCE_CONFIDENCE

        return score, level, reasons
