"""
run_prescription_demo.py

Interactive Demonstration Suite for Phase 6 Multi-Drug Prescription Safety Reasoning.
Executes all 6 required demo scenarios across different prescription sizes, duplicate handling,
unresolved items, and evidence prioritizations.
"""

import json
import logging
from pathlib import Path
from prescription_reasoning import PrescriptionSafetyReasoner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    project_root = Path(__file__).resolve().parent.parent
    graph_dir = project_root / "data" / "interim" / "graph"

    logger.info("Initializing PrescriptionSafetyReasoner for Phase 6 Live Demonstration...")
    reasoner = PrescriptionSafetyReasoner(graph_dir)
    reasoner.safety_engine.retriever.load()

    print("\n" + "="*90)
    print("PHASE 6 MULTI-DRUG PRESCRIPTION SAFETY REASONING & CLINICAL REPORTING DEMO")
    print("="*90)

    # -------------------------------------------------------------------------------------------------
    # DEMO 1: Single Drug Input (Graceful single-item handling)
    # -------------------------------------------------------------------------------------------------
    print("\n" + "#"*90)
    print("DEMO 1: SINGLE DRUG INPUT (Boundary Case: No Pairwise Evaluation)")
    print("#"*90)
    rep1 = reasoner.analyze_prescription(["fluconazole"], prescription_id="DEMO_01_SINGLE_DRUG")
    print(rep1.clinical_narrative_report)

    # -------------------------------------------------------------------------------------------------
    # DEMO 2: Two-Drug Prescription (Direct 1-pair comparison)
    # -------------------------------------------------------------------------------------------------
    print("\n" + "#"*90)
    print("DEMO 2: TWO-DRUG PRESCRIPTION (Cyclosporine + Fluconazole)")
    print("#"*90)
    rep2 = reasoner.analyze_prescription(["cyclosporine", "fluconazole"], prescription_id="DEMO_02_TWO_DRUGS")
    print(rep2.clinical_narrative_report)

    # -------------------------------------------------------------------------------------------------
    # DEMO 3: Three-Drug Prescription (3 Unique Pairs)
    # -------------------------------------------------------------------------------------------------
    print("\n" + "#"*90)
    print("DEMO 3: THREE-DRUG PRESCRIPTION (3 Unique Pairs: N*(N-1)/2 = 3)")
    print("#"*90)
    rep3 = reasoner.analyze_prescription(["cyclosporine", "fluconazole", "phentermine"], prescription_id="DEMO_03_THREE_DRUGS")
    print(rep3.clinical_narrative_report)

    # -------------------------------------------------------------------------------------------------
    # DEMO 4: Four-Drug Prescription (6 Unique Pairs)
    # -------------------------------------------------------------------------------------------------
    print("\n" + "#"*90)
    print("DEMO 4: FOUR-DRUG COMPLEX PRESCRIPTION (6 Unique Pairs: N*(N-1)/2 = 6)")
    print("#"*90)
    rep4 = reasoner.analyze_prescription(
        ["cyclosporine", "fluconazole", "phentermine", "trioxsalen"],
        prescription_id="DEMO_04_FOUR_DRUGS"
    )
    print(rep4.clinical_narrative_report)

    # -------------------------------------------------------------------------------------------------
    # DEMO 5: Duplicate and Mixed Identifier Formats (Canonical Collapsing)
    # -------------------------------------------------------------------------------------------------
    print("\n" + "#"*90)
    print("DEMO 5: DUPLICATE & MIXED IDENTIFIER FORMATS (Collapse Identical Canonical Entities)")
    print("#"*90)
    rep5 = reasoner.analyze_prescription(
        ["DRUG_000048", "CID000003365", "fluconazole", "DB00091", "cyclosporine"],
        prescription_id="DEMO_05_MIXED_AND_DUPLICATES"
    )
    print(rep5.clinical_narrative_report)

    # -------------------------------------------------------------------------------------------------
    # DEMO 6: Prescription with Unresolved Input & Negative Control
    # -------------------------------------------------------------------------------------------------
    print("\n" + "#"*90)
    print("DEMO 6: PRESCRIPTION WITH UNRESOLVED INPUT & NO DIRECT GRAPH EVIDENCE PAIR")
    print("#"*90)
    rep6 = reasoner.analyze_prescription(
        ["bivalirudin", "goserelin", "NonExistentNovelDrugXYZ_999"],
        prescription_id="DEMO_06_UNRESOLVED_AND_NEGATIVE"
    )
    print(rep6.clinical_narrative_report)

    print("\n" + "="*90)
    print("PHASE 6 MULTI-DRUG PRESCRIPTION DEMONSTRATION COMPLETED SUCCESSFULLY")
    print("="*90)

if __name__ == "__main__":
    main()
