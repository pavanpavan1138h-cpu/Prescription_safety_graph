"""
prescription_risk_engine.py

Prescription-Level Evidence Stratification Engine for Phase 6.
Determines overall prescription status:
- MULTI_SIGNAL_EVIDENCE
- CONVERGENT_EVIDENCE_PRESENT
- SINGLE_CHANNEL_EVIDENCE_PRESENT
- LIMITED_GRAPH_EVIDENCE
- NO_DIRECT_GRAPH_EVIDENCE
"""

from prescription_schema import (
    PrescriptionStatus,
    PrescriptionEvidenceSummary
)

class PrescriptionRiskEngine:
    @staticmethod
    def stratify_prescription(
        total_analyzed_pairs: int,
        convergent_count: int,
        ddi_only_count: int,
        combination_only_count: int,
        no_direct_count: int,
        unresolved_count: int = 0
    ) -> PrescriptionStatus:
        """
        Applies deterministic rules to classify overall prescription graph evidence status.
        """
        pairs_with_evidence = convergent_count + ddi_only_count + combination_only_count

        if total_analyzed_pairs == 0:
            if unresolved_count > 0:
                return PrescriptionStatus.LIMITED_GRAPH_EVIDENCE
            return PrescriptionStatus.NO_DIRECT_GRAPH_EVIDENCE

        # 1. Multi-signal: Multiple independent evidence-supported pairs (>1 positive pair)
        if pairs_with_evidence >= 2:
            return PrescriptionStatus.MULTI_SIGNAL_EVIDENCE

        # 2. Convergent: At least one pair has convergent evidence
        if convergent_count >= 1:
            return PrescriptionStatus.CONVERGENT_EVIDENCE_PRESENT

        # 3. Single-channel: Exactly one pair with DDI or combination events
        if pairs_with_evidence == 1:
            return PrescriptionStatus.SINGLE_CHANNEL_EVIDENCE_PRESENT

        # 4. Limited / No Direct Evidence
        if unresolved_count > 0:
            return PrescriptionStatus.LIMITED_GRAPH_EVIDENCE

        return PrescriptionStatus.NO_DIRECT_GRAPH_EVIDENCE
