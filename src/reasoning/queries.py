"""
safety_queries.py

High-level Query API for Phase 5 Prescription Safety Graph Reasoning.
Provides convenient entry points: evaluate_pair, lookup_drug, and explain_inference.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, List, Any

from src.reasoning.schemas import (
    DrugIdentity,
    SafetyInferenceResult,
    PairEvidenceBundle,
    EvidenceStatus
)
from src.reasoning.evidence_retrieval import EvidenceRetriever
from src.reasoning.safety_rules import SafetyRuleEngine
from src.reasoning.confidence_engine import ConfidenceEngine
from src.reasoning.explanation_engine import ExplanationEngine

logger = logging.getLogger(__name__)

class SafetyQueryEngine:
    def __init__(self, graph_dir: Optional[Path] = None):
        if graph_dir is None:
            project_root = Path(__file__).resolve().parent.parent.parent
            graph_dir = project_root / "data" / "interim" / "graph"
        self.graph_dir = graph_dir
        self.retriever = EvidenceRetriever(self.graph_dir)
        self._inference_cache: Dict[str, SafetyInferenceResult] = {}
        self._inference_counter = 1

    def lookup_drug(self, identifier: str) -> Optional[DrugIdentity]:
        """Resolves any identifier string (Internal ID, DrugBank ID, TWOSIDES CID, RxCUI, Name) to DrugIdentity."""
        return self.retriever.resolve_drug(identifier)

    def evaluate_pair(self, identifier_a: str, identifier_b: str) -> Optional[SafetyInferenceResult]:
        """
        Main query entry point: resolves both drug inputs, retrieves graph evidence,
        evaluates deterministic rules, computes confidence, and produces an explainable inference result.
        """
        drug_a = self.lookup_drug(identifier_a)
        drug_b = self.lookup_drug(identifier_b)

        if not drug_a or not drug_b:
            logger.warning(f"Could not resolve one or both drug inputs: '{identifier_a}', '{identifier_b}'.")
            return None

        # 1. Retrieve raw graph evidence
        bundle = self.retriever.retrieve_pair_evidence(drug_a.internal_drug_id, drug_b.internal_drug_id)

        # 2. Rule evaluation
        evidence_status, rule_fired = SafetyRuleEngine.evaluate_rules(bundle)

        # 3. Confidence calculation
        score, level, reasons = ConfidenceEngine.calculate_confidence(bundle, evidence_status)

        # 4. Synthesize explanation & trace
        inference_id = f"INF_{self._inference_counter:07d}"
        self._inference_counter += 1

        trace = ExplanationEngine.generate_trace(
            inference_id=inference_id,
            bundle=bundle,
            evidence_status=evidence_status,
            confidence_score=score,
            confidence_level=level,
            confidence_reasons=reasons,
            rule_fired=rule_fired
        )

        id_summary = f"{drug_a.entity_status} + {drug_b.entity_status}"

        result = SafetyInferenceResult(
            inference_id=inference_id,
            drug_a_id=drug_a.internal_drug_id,
            drug_b_id=drug_b.internal_drug_id,
            drug_pair_id=bundle.drug_pair_node_id,
            evidence_status=evidence_status,
            confidence_score=score,
            confidence_level=level,
            ddi_evidence_present=bool(bundle.ddi_records_forward or bundle.ddi_records_reverse),
            ddi_forward_count=len(bundle.ddi_records_forward),
            ddi_reverse_count=len(bundle.ddi_records_reverse),
            combination_event_present=(bundle.total_side_effects_count > 0),
            combination_event_count=bundle.total_side_effects_count,
            identity_status_summary=id_summary,
            inference_rule=rule_fired,
            reasoning_trace=trace
        )

        self._inference_cache[inference_id] = result
        return result

    def explain_inference(self, inference_id: str) -> Optional[str]:
        """Returns the formatted explanation text for a given inference ID."""
        res = self._inference_cache.get(inference_id)
        if res and res.reasoning_trace:
            return res.reasoning_trace.explanation_text
        return None
