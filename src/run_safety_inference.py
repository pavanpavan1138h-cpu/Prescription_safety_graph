"""
run_safety_inference.py

Batch Safety Inference Runner for Phase 5.
Executes reasoning over a structured cohort of drug pairs representing all major
evidence categories (Convergent, DDI-only, TWOSIDES-only, No-direct-evidence, Ambiguous).
Generates canonical outputs in data/interim/reasoning/.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict
import pandas as pd

from safety_queries import SafetyQueryEngine
from reasoning_schema import EvidenceStatus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    project_root = Path(__file__).resolve().parent.parent
    graph_dir = project_root / "data" / "interim" / "graph"
    reasoning_dir = project_root / "data" / "interim" / "reasoning"
    reasoning_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Initializing SafetyQueryEngine for batch inference run...")
    engine = SafetyQueryEngine(graph_dir)
    engine.retriever.load()

    # Define a diverse, representative cohort of drug pairs to evaluate
    logger.info("Assembling evaluation pair cohort...")
    
    # 1. Sample pairs with known DDIs from drug_interaction_edges.csv
    ddi_df = pd.read_csv(graph_dir / "drug_interaction_edges.csv", nrows=100)
    ddi_pairs = ddi_df[["source_node_id", "target_node_id"]].drop_duplicates().values.tolist()

    # 2. Sample pairs with known TWOSIDES combinations from drug_pair_nodes.csv
    pair_nodes_df = pd.read_csv(graph_dir / "drug_pair_nodes.csv", nrows=100)
    twosides_pairs = []
    for _, r in pair_nodes_df.iterrows():
        props = json.loads(r["properties_json"])
        d1 = props.get("drug1_internal_id")
        d2 = props.get("drug2_internal_id")
        if d1 and d2:
            twosides_pairs.append([d1, d2])

    # 3. Add explicit test cases including negative controls and ambiguous mapping entities
    explicit_cases = [
        ["DRUG_000045", "DRUG_000048"], # Phentermine + Fluconazole (TWOSIDES combination)
        ["DRUG_001202", "DRUG_000302"], # Trioxsalen + Verteporfin (DrugBank DDI)
        ["DRUG_000001", "DRUG_000002"], # Bivalirudin + Goserelin (Negative control / no direct DDI)
        ["DRUG_000003", "DRUG_000004"], # Gramicidin + DDAVP (Negative control)
        ["DRUG_000006", "DRUG_000048"], # Cyclosporine + Fluconazole (Known major convergent interaction)
    ]

    all_pairs = []
    seen = set()
    for p in (explicit_cases + ddi_pairs[:50] + twosides_pairs[:50]):
        sorted_p = tuple(sorted([p[0], p[1]]))
        if sorted_p not in seen and p[0] != p[1]:
            seen.add(sorted_p)
            all_pairs.append([p[0], p[1]])

    logger.info(f"Evaluating reasoning engine across {len(all_pairs)} unique drug pairs...")

    inference_results_rows = []
    inference_evidence_rows = []
    explanations_dict = {}

    evidence_id_counter = 1
    for pair in all_pairs:
        res = engine.evaluate_pair(pair[0], pair[1])
        if not res:
            continue

        inference_results_rows.append({
            "inference_id": res.inference_id,
            "drug_a_id": res.drug_a_id,
            "drug_b_id": res.drug_b_id,
            "drug_pair_id": res.drug_pair_id or "NONE",
            "evidence_status": res.evidence_status.value,
            "confidence_score": res.confidence_score,
            "confidence_level": res.confidence_level.value,
            "ddi_evidence_present": res.ddi_evidence_present,
            "ddi_forward_count": res.ddi_forward_count,
            "ddi_reverse_count": res.ddi_reverse_count,
            "combination_event_present": res.combination_event_present,
            "combination_event_count": res.combination_event_count,
            "identity_status": res.identity_status_summary,
            "inference_rule": res.inference_rule,
            "clinical_interpretation": res.clinical_interpretation
        })

        if res.reasoning_trace:
            explanations_dict[res.inference_id] = {
                "drug_a_id": res.drug_a_id,
                "drug_b_id": res.drug_b_id,
                "evidence_status": res.evidence_status.value,
                "confidence_level": res.confidence_level.value,
                "confidence_score": res.confidence_score,
                "rule_fired": res.reasoning_trace.rule_fired,
                "graph_paths": res.reasoning_trace.graph_paths,
                "supporting_edge_ids": res.reasoning_trace.supporting_edge_ids,
                "source_record_ids": res.reasoning_trace.source_record_ids,
                "confidence_reasons": res.reasoning_trace.confidence_reasons,
                "explanation_text": res.reasoning_trace.explanation_text
            }

            for edge_id in res.reasoning_trace.supporting_edge_ids:
                inference_evidence_rows.append({
                    "inference_id": res.inference_id,
                    "evidence_id": f"EV_{evidence_id_counter:07d}",
                    "evidence_type": "SUPPORTING_GRAPH_EDGE",
                    "graph_edge_id": edge_id,
                    "source_node_id": res.drug_a_id,
                    "target_node_id": res.drug_b_id
                })
                evidence_id_counter += 1

    # Write CSVs and JSONs
    pd.DataFrame(inference_results_rows).to_csv(reasoning_dir / "safety_inference_results.csv", index=False)
    pd.DataFrame(inference_evidence_rows).to_csv(reasoning_dir / "safety_inference_evidence.csv", index=False)
    
    with open(reasoning_dir / "safety_inference_explanations.json", "w") as f:
        json.dump(explanations_dict, f, indent=4)

    res_df = pd.DataFrame(inference_results_rows)
    summary = {
        "total_pairs_evaluated": len(res_df),
        "evidence_status_distribution": res_df["evidence_status"].value_counts().to_dict(),
        "confidence_level_distribution": res_df["confidence_level"].value_counts().to_dict(),
        "ddi_supported_pairs_count": int(res_df["ddi_evidence_present"].sum()),
        "twosides_supported_pairs_count": int(res_df["combination_event_present"].sum()),
        "convergent_evidence_pairs_count": int((res_df["evidence_status"] == EvidenceStatus.CONVERGENT_SAFETY_EVIDENCE.value).sum()),
        "total_supporting_evidence_records": len(inference_evidence_rows)
    }

    with open(reasoning_dir / "safety_reasoning_summary.json", "w") as f:
        json.dump(summary, f, indent=4)

    logger.info(f"Phase 5 Batch Inference complete. Evaluated {len(res_df)} pairs. Outputs saved to {reasoning_dir}.")

if __name__ == "__main__":
    main()
