"""
clinical_report_generator.py

Clinical Safety Report Generator for Phase 6.
Generates human-readable structured clinical narratives and complete machine-readable reports.
"""

from typing import List, Dict, Any
from src.prescription.schemas import (
    PrescriptionSafetyReport,
    PrescriptionResolutionResult,
    PrescriptionEvidenceSummary,
    PrioritizedFinding,
    DrugParticipationSummary
)

class ClinicalReportGenerator:
    @staticmethod
    def generate_narrative_report(
        prescription_id: str,
        generated_at: str,
        res_summary: PrescriptionResolutionResult,
        ev_summary: PrescriptionEvidenceSummary,
        drug_participation: List[DrugParticipationSummary],
        findings: List[PrioritizedFinding]
    ) -> str:
        """
        Creates a structured, multi-section, human-readable clinical safety report text.
        """
        lines = []
        lines.append("="*85)
        lines.append(f"PRESCRIPTION SAFETY EVIDENCE & REASONING REPORT [{prescription_id}]")
        lines.append(f"Generated At: {generated_at}")
        lines.append("="*85)

        # Section 1: Prescription Input & Identity Resolution
        lines.append("\n[1] PRESCRIPTION IDENTITY RESOLUTION SUMMARY")
        lines.append(f"  * Total Input Items:            {ev_summary.total_input_items}")
        lines.append(f"  * Unique Canonical Drugs:       {ev_summary.unique_canonical_drugs}")
        lines.append(f"  * Duplicate Inputs Collapsed:   {ev_summary.duplicates_collapsed_count}")
        lines.append(f"  * Ambiguous Mappings Detected:  {ev_summary.ambiguous_items_count}")
        lines.append(f"  * Unresolved Input Items:       {ev_summary.unresolved_items_count}")

        lines.append("  * Resolved Medication List:")
        for d in res_summary.resolved_drugs:
            if d.resolved_internal_drug_id:
                rx_str = f", RxCUI: {d.rxcui}" if d.rxcui else ""
                lines.append(f"    - '{d.original_input}' -> {d.display_name} ({d.resolved_internal_drug_id}) [{d.resolution_status.value}{rx_str}]")
            else:
                lines.append(f"    - '{d.original_input}' -> UNRESOLVED (No graph entity match)")

        # Section 2: Pairwise Safety Analysis Summary
        lines.append("\n[2] PAIRWISE GRAPH SAFETY ANALYSIS SUMMARY")
        lines.append(f"  * Expected Unique Combinations: {ev_summary.total_expected_pairs}")
        lines.append(f"  * Evaluated Pairs:              {ev_summary.total_analyzed_pairs}")
        lines.append(f"  * Pairs with Graph Evidence:    {ev_summary.pairs_with_evidence}")
        lines.append(f"  * Overall Prescription Status:  {ev_summary.prescription_status.value}")
        lines.append("  * Evidence Distribution:")
        lines.append(f"    - Convergent Safety Evidence:        {ev_summary.convergent_evidence_pairs}")
        lines.append(f"    - DrugBank DDI Evidence Only:        {ev_summary.ddi_only_pairs}")
        lines.append(f"    - TWOSIDES Combination Events Only:  {ev_summary.combination_event_only_pairs}")
        lines.append(f"    - No Direct Evidence in Graph:       {ev_summary.no_direct_evidence_pairs}")

        # Section 3: Prioritized Findings
        lines.append("\n[3] PRIORITIZED SAFETY FINDINGS (Ranked by Graph Evidence Strength)")
        if not findings:
            lines.append("  * No pairwise findings evaluated (fewer than 2 unique resolved drugs).")
        else:
            for idx, f in enumerate(findings, 1):
                lines.append(f"  ({idx}) [{f.evidence_priority.value}] {f.drug_a_name} + {f.drug_b_name}")
                lines.append(f"      - Evidence Status:  {f.evidence_status}")
                lines.append(f"      - Confidence Level: {f.confidence_level} (Score: {f.confidence_score})")
                lines.append(f"      - Evidence Counts:  DDI Assertions: {f.ddi_count}, TWOSIDES Adverse Events: {f.event_count}")
                lines.append(f"      - Inference ID:     {f.inference_id} ({f.rule_fired})")
                if f.supporting_edge_ids:
                    sample_edges = ", ".join(f.supporting_edge_ids[:3])
                    extra = f" (+{len(f.supporting_edge_ids)-3} more)" if len(f.supporting_edge_ids) > 3 else ""
                    lines.append(f"      - Supporting Edges: {sample_edges}{extra}")

        # Section 4: Drug Participation Analysis
        lines.append("\n[4] DRUG PARTICIPATION & EVIDENCE INVOLVEMENT")
        for dp in drug_participation:
            lines.append(
                f"  * {dp.display_name} ({dp.internal_drug_id}): "
                f"Involved in {dp.total_pairs_involved} pairs ({dp.evidence_supported_pairs} with evidence "
                f"-> {dp.convergent_pairs} convergent, {dp.ddi_only_pairs} DDI, {dp.combination_event_pairs} events)"
            )

        # Section 5: Scientific & Clinical Guardrails
        lines.append("\n[5] SCIENTIFIC LIMITATIONS & ETHICAL NOTICE")
        lines.append("  * NOTICE 1: Graph evidence priority reflects evidence density, not calibrated patient-specific clinical severity.")
        lines.append("  * NOTICE 2: Absence of direct evidence in the current knowledge graph is NOT proof of clinical safety.")
        lines.append("  * NOTICE 3: Drug interaction assertions and observational adverse event associations do not independently establish causality.")
        lines.append("  * NOTICE 4: This automated report is generated strictly from integrated biomedical datasets and does not replace clinical consultation.")
        lines.append("="*85)

        return "\n".join(lines)
