"""
explanation_engine.py

Explanation Engine for Phase 5.
Generates human-readable reasoning narratives and multi-hop graph path traces.
"""

from typing import List, Dict
from src.reasoning.schemas import (
    PairEvidenceBundle,
    EvidenceStatus,
    ConfidenceLevel,
    ReasoningTrace
)

class ExplanationEngine:
    @staticmethod
    def generate_trace(
        inference_id: str,
        bundle: PairEvidenceBundle,
        evidence_status: EvidenceStatus,
        confidence_score: float,
        confidence_level: ConfidenceLevel,
        confidence_reasons: List[str],
        rule_fired: str
    ) -> ReasoningTrace:
        drug_a = bundle.drug_a
        drug_b = bundle.drug_b
        
        name_a = drug_a.display_name or drug_a.internal_drug_id
        name_b = drug_b.display_name or drug_b.internal_drug_id

        graph_paths = []
        supporting_edge_ids = []
        source_record_ids = []

        explanation_lines = [
            f"EVALUATION FOR DRUG PAIR: {name_a} ({drug_a.internal_drug_id}) + {name_b} ({drug_b.internal_drug_id})",
            f"Evidence Classification: {evidence_status.value}",
            f"Evidence Confidence: {confidence_level.value} (Score: {confidence_score})"
        ]

        # 1. DDI Paths & Evidence
        all_ddi = bundle.ddi_records_forward + bundle.ddi_records_reverse
        if all_ddi:
            explanation_lines.append("\n[1] DIRECT DRUGBANK DDI ASSERTIONS:")
            for ddi in all_ddi:
                supporting_edge_ids.append(ddi.edge_id)
                source_record_ids.append(f"DDI:{ddi.source_drugbank_id_1}:{ddi.source_drugbank_id_2}")
                path_str = f"({ddi.source_drug_id}) -[:INTERACTS_WITH]-> ({ddi.target_drug_id})"
                graph_paths.append(path_str)
                explanation_lines.append(f"  * Directed Path: {path_str} [Edge: {ddi.edge_id}]")
                explanation_lines.append(f"    Source IDs: {ddi.source_drugbank_id_1} -> {ddi.source_drugbank_id_2}")
                explanation_lines.append(f"    Description: {ddi.interaction_description}")

        # 2. Combination Adverse Event Paths & Evidence
        if bundle.drug_pair_node_id and bundle.total_side_effects_count > 0:
            explanation_lines.append(f"\n[2] TWOSIDES COMBINATION SAFETY OBSERVATIONS ({bundle.total_side_effects_count} total events):")
            pair_path = f"({drug_a.internal_drug_id}) -> [{bundle.drug_pair_node_id}] <- ({drug_b.internal_drug_id})"
            graph_paths.append(pair_path)
            explanation_lines.append(f"  * Reified Observation Node: {bundle.drug_pair_node_id}")
            explanation_lines.append("  * Sample Observed Adverse Events:")
            
            for se in bundle.side_effect_records[:5]: # Top 5 samples
                supporting_edge_ids.append(se.edge_id)
                source_record_ids.append(f"TWOSIDES_EVENT:{se.source_drug_1}:{se.source_drug_2}:{se.side_effect_id}")
                explanation_lines.append(f"    - {se.side_effect_name} (SE_{se.side_effect_id}) [Edge: {se.edge_id}]")

        # 3. Clinical Identity Context
        explanation_lines.append("\n[3] CLINICAL IDENTITY CONTEXT:")
        rx_a = f"RXCUI_{drug_a.rxcui} ({drug_a.rxnorm_name})" if drug_a.rxcui else "Unresolved / No direct RxCUI"
        rx_b = f"RXCUI_{drug_b.rxcui} ({drug_b.rxnorm_name})" if drug_b.rxcui else "Unresolved / No direct RxCUI"
        explanation_lines.append(f"  * {drug_a.internal_drug_id}: {rx_a}")
        explanation_lines.append(f"  * {drug_b.internal_drug_id}: {rx_b}")

        # 4. Confidence Explanation
        explanation_lines.append("\n[4] CONFIDENCE ASSESSMENT RATIONALE:")
        for r in confidence_reasons:
            explanation_lines.append(f"  * {r}")

        # 5. Scientific Guardrail
        explanation_lines.append("\n[5] SCIENTIFIC INTERPRETATION NOTICE:")
        if evidence_status == EvidenceStatus.NO_DIRECT_GRAPH_EVIDENCE:
            explanation_lines.append(
                "  * NOTE: No direct interaction or combination safety signal exists in the current graph. "
                "This indicates absence of evidence in the ingested datasets, NOT confirmation of medical safety."
            )
        else:
            explanation_lines.append(
                "  * NOTE: Findings represent documented pharmacological statements and observational safety associations. "
                "They do not constitute calibrated patient-specific clinical risk predictions or medical treatment advice."
            )

        explanation_text = "\n".join(explanation_lines)

        return ReasoningTrace(
            inference_id=inference_id,
            graph_paths=graph_paths,
            supporting_edge_ids=supporting_edge_ids,
            source_record_ids=source_record_ids,
            rule_fired=rule_fired,
            confidence_reasons=confidence_reasons,
            explanation_text=explanation_text
        )
