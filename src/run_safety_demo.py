"""
run_safety_demo.py

Interactive Demonstration of Phase 5 Prescription Safety Graph Reasoning.
Executes the 6 required real graph reasoning queries across all evidence categories.
"""

import json
import logging
from pathlib import Path
from safety_queries import SafetyQueryEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    project_root = Path(__file__).resolve().parent.parent
    graph_dir = project_root / "data" / "interim" / "graph"

    logger.info("Initializing SafetyQueryEngine for Phase 5 Reasoning Demonstration...")
    engine = SafetyQueryEngine(graph_dir)
    engine.retriever.load()

    print("\n" + "="*85)
    print("PHASE 5 PRESCRIPTION SAFETY GRAPH REASONING & INFERENCE DEMONSTRATION")
    print("="*85)

    # Query 1: DrugBank ID lookup
    q1_id = "DB00191"
    drug_1 = engine.lookup_drug(q1_id)
    print(f"\n[QUERY 1] Drug Lookup by DrugBank ID '{q1_id}':")
    print(f"  Internal ID:    {drug_1.internal_drug_id}")
    print(f"  Display Name:   {drug_1.display_name}")
    print(f"  Entity Status:  {drug_1.entity_status}")
    print(f"  RxNorm Concept: RXCUI_{drug_1.rxcui} ({drug_1.rxnorm_name})")

    # Query 2: TWOSIDES CID lookup
    q2_id = "CID000003365"
    drug_2 = engine.lookup_drug(q2_id)
    print(f"\n[QUERY 2] Drug Lookup by TWOSIDES CID '{q2_id}':")
    print(f"  Internal ID:    {drug_2.internal_drug_id}")
    print(f"  Display Name:   {drug_2.display_name}")
    print(f"  Entity Status:  {drug_2.entity_status}")
    print(f"  RxNorm Concept: RXCUI_{drug_2.rxcui} ({drug_2.rxnorm_name})")

    # Query 3: Known pair with DDI_EVIDENCE_ONLY
    # DRUG_001202 (trioxsalen) + DRUG_000302 (verteporfin)
    res_ddi = engine.evaluate_pair("DRUG_001202", "DRUG_000302")
    print(f"\n[QUERY 3] Drug Pair Evaluation: DDI_EVIDENCE_ONLY Category:")
    print(f"  Pair:            DRUG_001202 (trioxsalen) + DRUG_000302 (verteporfin)")
    print(f"  Evidence Status: {res_ddi.evidence_status.value}")
    print(f"  Confidence:      {res_ddi.confidence_level.value} (Score: {res_ddi.confidence_score})")
    print(f"  DDI Present:     {res_ddi.ddi_evidence_present} (Forward: {res_ddi.ddi_forward_count}, Reverse: {res_ddi.ddi_reverse_count})")
    print(f"  Events Present:  {res_ddi.combination_event_present}")
    print(f"  Rule Fired:      {res_ddi.inference_rule}")
    print(f"\n  --- Reasoning Explanation Trace ---")
    print(engine.explain_inference(res_ddi.inference_id))

    # Query 4: Known pair with COMBINATION_EVENT_EVIDENCE_ONLY
    # DRUG_000045 (Phentermine) + DRUG_000048 (Fluconazole)
    res_event = engine.evaluate_pair("DRUG_000045", "DRUG_000048")
    print(f"\n" + "-"*85)
    print(f"[QUERY 4] Drug Pair Evaluation: COMBINATION_EVENT_EVIDENCE_ONLY Category:")
    print(f"  Pair:            DRUG_000045 (Phentermine) + DRUG_000048 (Fluconazole)")
    print(f"  Evidence Status: {res_event.evidence_status.value}")
    print(f"  Confidence:      {res_event.confidence_level.value} (Score: {res_event.confidence_score})")
    print(f"  DDI Present:     {res_event.ddi_evidence_present}")
    print(f"  Events Present:  {res_event.combination_event_present} ({res_event.combination_event_count} total events)")
    print(f"  Rule Fired:      {res_event.inference_rule}")
    print(f"\n  --- Reasoning Explanation Trace ---")
    print(engine.explain_inference(res_event.inference_id))

    # Query 5: Known pair with CONVERGENT_SAFETY_EVIDENCE
    # DRUG_000006 (cyclosporine) + DRUG_000048 (fluconazole)
    res_conv = engine.evaluate_pair("DRUG_000006", "DRUG_000048")
    print(f"\n" + "-"*85)
    print(f"[QUERY 5] Drug Pair Evaluation: CONVERGENT_SAFETY_EVIDENCE Category:")
    print(f"  Pair:            DRUG_000006 (cyclosporine) + DRUG_000048 (fluconazole)")
    print(f"  Evidence Status: {res_conv.evidence_status.value}")
    print(f"  Confidence:      {res_conv.confidence_level.value} (Score: {res_conv.confidence_score})")
    print(f"  DDI Present:     {res_conv.ddi_evidence_present} (Forward: {res_conv.ddi_forward_count}, Reverse: {res_conv.ddi_reverse_count})")
    print(f"  Events Present:  {res_conv.combination_event_present} ({res_conv.combination_event_count} total events)")
    print(f"  Rule Fired:      {res_conv.inference_rule}")
    print(f"\n  --- Reasoning Explanation Trace ---")
    print(engine.explain_inference(res_conv.inference_id))

    # Query 6: Pair with NO_DIRECT_GRAPH_EVIDENCE (Negative control)
    # DRUG_000001 (bivalirudin) + DRUG_000002 (goserelin)
    res_none = engine.evaluate_pair("DRUG_000001", "DRUG_000002")
    print(f"\n" + "-"*85)
    print(f"[QUERY 6] Drug Pair Evaluation: NO_DIRECT_GRAPH_EVIDENCE Category:")
    print(f"  Pair:            DRUG_000001 (bivalirudin) + DRUG_000002 (goserelin)")
    print(f"  Evidence Status: {res_none.evidence_status.value}")
    print(f"  Confidence:      {res_none.confidence_level.value} (Score: {res_none.confidence_score})")
    print(f"  DDI Present:     {res_none.ddi_evidence_present}")
    print(f"  Events Present:  {res_none.combination_event_present}")
    print(f"  Rule Fired:      {res_none.inference_rule}")
    print(f"\n  --- Reasoning Explanation Trace ---")
    print(engine.explain_inference(res_none.inference_id))

    print("\n" + "="*85)
    print("PHASE 5 REASONING DEMONSTRATION COMPLETED SUCCESSFULLY")
    print("="*85)

if __name__ == "__main__":
    main()
