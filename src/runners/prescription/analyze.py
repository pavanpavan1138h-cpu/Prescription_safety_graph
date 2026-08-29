"""
run_prescription_analysis.py

Batch Execution Runner for Phase 6 Multi-Drug Prescription Safety Reasoning.
Evaluates a diverse suite of test prescriptions across different sizes (1, 2, 3, 4, 5+ drugs),
duplicate handling, mixed identifier formats, and negative controls.
Generates canonical outputs in data/interim/prescription_reasoning/.
"""

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import List, Dict
import pandas as pd

from src.prescription.reasoning import PrescriptionSafetyReasoner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    graph_dir = project_root / "data" / "interim" / "graph"
    out_dir = project_root / "data" / "interim" / "prescription_reasoning"
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Initializing PrescriptionSafetyReasoner for batch analysis...")
    reasoner = PrescriptionSafetyReasoner(graph_dir)
    reasoner.safety_engine.retriever.load()

    # Define diverse test cohort of prescriptions
    test_prescriptions = [
        # Prescription 1: Single drug (boundary case)
        {
            "id": "RX_001_SINGLE_DRUG",
            "medications": ["fluconazole"]
        },
        # Prescription 2: Known convergent pair
        {
            "id": "RX_002_CONVERGENT_PAIR",
            "medications": ["cyclosporine", "fluconazole"]
        },
        # Prescription 3: 3-Drug Multi-Signal Prescription
        {
            "id": "RX_003_THREE_DRUGS",
            "medications": ["cyclosporine", "fluconazole", "phentermine"]
        },
        # Prescription 4: 4-Drug Complex Polypharmacy Prescription
        {
            "id": "RX_004_FOUR_DRUGS",
            "medications": ["cyclosporine", "fluconazole", "phentermine", "trioxsalen"]
        },
        # Prescription 5: Duplicate and mixed identifier formats
        {
            "id": "RX_005_MIXED_AND_DUPLICATES",
            "medications": ["DRUG_000048", "CID000003365", "fluconazole", "DB00091", "cyclosporine"]
        },
        # Prescription 6: Prescription with Unresolved input and negative control
        {
            "id": "RX_006_UNRESOLVED_AND_NEGATIVE",
            "medications": ["bivalirudin", "goserelin", "UnknownSyntheticMedXYZ_99"]
        },
        # Prescription 7: 5-Drug Comprehensive Multi-channel Prescription
        {
            "id": "RX_007_FIVE_DRUGS",
            "medications": ["DRUG_000001", "DRUG_000006", "DRUG_000045", "DRUG_000048", "DRUG_001202"]
        }
    ]

    logger.info(f"Executing batch analysis across {len(test_prescriptions)} test prescriptions...")

    all_reports_json = []
    all_pair_results_rows = []
    all_signals_rows = []
    all_failures_rows = []

    for rx in test_prescriptions:
        rx_id = rx["id"]
        meds = rx["medications"]
        report = reasoner.analyze_prescription(meds, prescription_id=rx_id)

        # 1. Store Pair Results
        for pr in report.pair_results:
            all_pair_results_rows.append({
                "prescription_id": rx_id,
                "pair_index": pr["pair_index"],
                "canonical_pair_key": pr["canonical_pair_key"],
                "drug_a_id": pr["drug_a_id"],
                "drug_b_id": pr["drug_b_id"],
                "drug_a_name": pr["drug_a_name"],
                "drug_b_name": pr["drug_b_name"],
                "evidence_status": pr["evidence_status"],
                "confidence_level": pr["confidence_level"],
                "confidence_score": pr["confidence_score"],
                "ddi_present": pr["ddi_present"],
                "ddi_count": pr["ddi_forward_count"] + pr["ddi_reverse_count"],
                "events_present": pr["events_present"],
                "event_count": pr["event_count"],
                "inference_id": pr["inference_id"],
                "rule_fired": pr["rule_fired"]
            })

        # 2. Store Signals / Prioritized findings
        for f in report.prioritized_findings:
            all_signals_rows.append({
                "prescription_id": rx_id,
                "finding_id": f.finding_id,
                "pair_index": f.pair_index,
                "drug_a_id": f.drug_a_id,
                "drug_b_id": f.drug_b_id,
                "drug_a_name": f.drug_a_name,
                "drug_b_name": f.drug_b_name,
                "evidence_status": f.evidence_status,
                "evidence_priority": f.evidence_priority.value,
                "confidence_level": f.confidence_level,
                "confidence_score": f.confidence_score,
                "ddi_present": f.ddi_present,
                "ddi_count": f.ddi_count,
                "events_present": f.events_present,
                "event_count": f.event_count,
                "inference_id": f.inference_id,
                "rule_fired": f.rule_fired,
                "supporting_edge_ids": str(f.supporting_edge_ids),
                "source_record_ids": str(f.source_record_ids)
            })

        # 3. Store Failures/Unresolved
        for unres in report.resolution_summary.unresolved_inputs:
            all_failures_rows.append({
                "prescription_id": rx_id,
                "unresolved_input": unres,
                "failure_reason": "NO_MATCHING_GRAPH_ENTITY"
            })

        # 4. JSON structure
        all_reports_json.append({
            "prescription_id": report.prescription_id,
            "generated_at": report.generated_at,
            "resolution_summary": {
                "original_inputs": report.resolution_summary.original_inputs,
                "canonical_drug_ids": report.resolution_summary.canonical_drug_ids,
                "unresolved_inputs": report.resolution_summary.unresolved_inputs,
                "ambiguous_inputs": report.resolution_summary.ambiguous_inputs,
                "duplicate_inputs": report.resolution_summary.duplicate_inputs,
                "resolved_drugs": [asdict(d) for d in report.resolution_summary.resolved_drugs]
            },
            "evidence_summary": asdict(report.evidence_summary),
            "drug_participation": [asdict(dp) for dp in report.drug_participation],
            "prioritized_findings": [asdict(f) for f in report.prioritized_findings],
            "pair_results": report.pair_results,
            "clinical_narrative_report": report.clinical_narrative_report,
            "scientific_limitations": report.scientific_limitations
        })

    # Write files
    with open(out_dir / "prescription_safety_reports.json", "w") as f:
        json.dump(all_reports_json, f, indent=4)

    pd.DataFrame(all_pair_results_rows).to_csv(out_dir / "prescription_pair_results.csv", index=False)
    pd.DataFrame(all_signals_rows).to_csv(out_dir / "prescription_signals.csv", index=False)
    pd.DataFrame(all_failures_rows).to_csv(out_dir / "prescription_failures.csv", index=False)

    summary_metrics = {
        "total_prescriptions_analyzed": len(test_prescriptions),
        "total_pairwise_evaluations": len(all_pair_results_rows),
        "total_prioritized_signals": len(all_signals_rows),
        "total_unresolved_inputs": len(all_failures_rows),
        "prescription_status_distribution": pd.Series([r["evidence_summary"]["prescription_status"] for r in all_reports_json]).value_counts().to_dict(),
        "priority_distribution": pd.Series([s["evidence_priority"] for s in all_signals_rows]).value_counts().to_dict() if all_signals_rows else {}
    }

    with open(out_dir / "prescription_reasoning_summary.json", "w") as f:
        json.dump(summary_metrics, f, indent=4)

    logger.info(f"Phase 6 Batch Prescription Analysis completed. Saved outputs to {out_dir}.")

if __name__ == "__main__":
    main()
