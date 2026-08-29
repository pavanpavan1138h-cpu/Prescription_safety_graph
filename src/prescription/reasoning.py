"""
prescription_reasoning.py

Master Orchestrator for Phase 6 Multi-Drug Prescription Safety Reasoning.
Combines resolver, pair generator, Phase 5 pairwise reasoner, aggregator, prioritizer, and reporter.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

from src.prescription.schemas import (
    PrescriptionSafetyReport,
    PrescriptionResolutionResult,
    PrescriptionEvidenceSummary,
    PrioritizedFinding,
    DrugParticipationSummary
)
from src.prescription.resolver import PrescriptionResolver
from src.prescription.pair_generator import PrescriptionPairGenerator
from src.prescription.prioritization import SignalPrioritizer
from src.prescription.aggregation import PrescriptionAggregator
from src.prescription.report_generator import ClinicalReportGenerator
from src.reasoning.queries import SafetyQueryEngine

logger = logging.getLogger(__name__)

class PrescriptionSafetyReasoner:
    def __init__(self, graph_dir: Optional[Path] = None):
        if graph_dir is None:
            project_root = Path(__file__).resolve().parent.parent.parent
            graph_dir = project_root / "data" / "interim" / "graph"
        self.graph_dir = graph_dir
        
        self.safety_engine = SafetyQueryEngine(self.graph_dir)
        self.resolver = PrescriptionResolver(self.safety_engine.retriever)
        self._prescription_counter = 1

    def analyze_prescription(self, medications: List[str], prescription_id: Optional[str] = None) -> PrescriptionSafetyReport:
        """
        Main entry point for evaluating an entire multi-drug prescription list.
        """
        if prescription_id is None:
            prescription_id = f"RX_REPORT_{self._prescription_counter:06d}"
            self._prescription_counter += 1

        generated_at = datetime.now().isoformat()

        # 1. Identity Resolution
        res_summary = self.resolver.resolve_prescription(medications)

        # Build drug name map for resolved drugs
        drug_name_map = {}
        for d in res_summary.resolved_drugs:
            if d.resolved_internal_drug_id:
                drug_name_map[d.resolved_internal_drug_id] = d.display_name or d.resolved_internal_drug_id

        # 2. Generate Pairs
        pairs = PrescriptionPairGenerator.generate_pairs(res_summary.canonical_drug_ids, drug_name_map)

        # 3. Evaluate each pair via Phase 5 pairwise engine
        pair_inferences = []
        raw_pair_results = []

        for p in pairs:
            res = self.safety_engine.evaluate_pair(p.drug_a_id, p.drug_b_id)
            if res:
                pair_inferences.append((p.pair_index, res, p.drug_a_name, p.drug_b_name))
                raw_pair_results.append({
                    "pair_index": p.pair_index,
                    "canonical_pair_key": p.canonical_pair_key,
                    "drug_a_id": p.drug_a_id,
                    "drug_b_id": p.drug_b_id,
                    "drug_a_name": p.drug_a_name,
                    "drug_b_name": p.drug_b_name,
                    "evidence_status": res.evidence_status.value,
                    "confidence_level": res.confidence_level.value,
                    "confidence_score": res.confidence_score,
                    "ddi_present": res.ddi_evidence_present,
                    "ddi_forward_count": res.ddi_forward_count,
                    "ddi_reverse_count": res.ddi_reverse_count,
                    "events_present": res.combination_event_present,
                    "event_count": res.combination_event_count,
                    "inference_id": res.inference_id,
                    "rule_fired": res.inference_rule
                })

        # 4. Aggregate Prescription Evidence
        ev_summary, drug_participation = PrescriptionAggregator.aggregate_evidence(
            res_summary=res_summary,
            pair_inferences=pair_inferences,
            drug_name_map=drug_name_map
        )

        # 5. Prioritize Findings
        prioritized_findings = SignalPrioritizer.prioritize_findings(pair_inferences)

        # 6. Generate Narrative Report
        narrative_report = ClinicalReportGenerator.generate_narrative_report(
            prescription_id=prescription_id,
            generated_at=generated_at,
            res_summary=res_summary,
            ev_summary=ev_summary,
            drug_participation=drug_participation,
            findings=prioritized_findings
        )

        return PrescriptionSafetyReport(
            prescription_id=prescription_id,
            generated_at=generated_at,
            resolution_summary=res_summary,
            evidence_summary=ev_summary,
            drug_participation=drug_participation,
            prioritized_findings=prioritized_findings,
            pair_results=raw_pair_results,
            clinical_narrative_report=narrative_report
        )
