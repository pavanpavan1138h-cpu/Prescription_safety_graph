"""
safety_rules.py

Deterministic Safety Rule Engine for Phase 5.
Categorizes drug pair evidence bundles into explicit evidence classes:
- CONVERGENT_SAFETY_EVIDENCE
- DDI_EVIDENCE_ONLY
- COMBINATION_EVENT_EVIDENCE_ONLY
- NO_DIRECT_GRAPH_EVIDENCE
"""

from typing import Tuple
from reasoning_schema import (
    PairEvidenceBundle,
    EvidenceStatus
)

class SafetyRuleEngine:
    @staticmethod
    def evaluate_rules(bundle: PairEvidenceBundle) -> Tuple[EvidenceStatus, str]:
        """
        Applies deterministic rules to classify evidence presence.
        Returns (EvidenceStatus, rule_name_fired).
        """
        has_ddi = bool(bundle.ddi_records_forward or bundle.ddi_records_reverse)
        has_events = bool(bundle.side_effect_records or bundle.total_side_effects_count > 0)

        # Rule 1: Convergent Evidence
        if has_ddi and has_events:
            return (
                EvidenceStatus.CONVERGENT_SAFETY_EVIDENCE,
                "RULE_CONVERGENT_SAFETY_EVIDENCE"
            )

        # Rule 2: DDI Evidence Only
        if has_ddi and not has_events:
            return (
                EvidenceStatus.DDI_EVIDENCE_ONLY,
                "RULE_DDI_EVIDENCE_ONLY"
            )

        # Rule 3: Combination Events Evidence Only
        if not has_ddi and has_events:
            return (
                EvidenceStatus.COMBINATION_EVENT_EVIDENCE_ONLY,
                "RULE_COMBINATION_EVENT_EVIDENCE_ONLY"
            )

        # Rule 4: No Direct Graph Evidence
        return (
            EvidenceStatus.NO_DIRECT_GRAPH_EVIDENCE,
            "RULE_NO_DIRECT_GRAPH_EVIDENCE"
        )
